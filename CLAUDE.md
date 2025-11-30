# CLAUDE.md - AI Assistant Guide for BetterTouchTool MCP Server

## Repository Overview

This is a **Model Context Protocol (MCP) server** that enables AI assistants like Claude to control and interact with BetterTouchTool on macOS. The server acts as a bridge between MCP-compatible AI clients and the BetterTouchTool application, exposing BTT's functionality through 20 specialized tools.

**Key Purpose**: Enable AI-driven automation, configuration management, and understanding of BetterTouchTool setups through a standardized protocol.

**Technology Stack**:
- **Language**: Python 3.12+
- **MCP Framework**: FastMCP (wrapper around official MCP SDK)
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic v2
- **Package Manager**: uv (modern Python package manager)

## Repository Structure

```
bettertouchtool-mcp-server/
├── btt_mcp.py          # Single-file MCP server implementation
├── pyproject.toml      # Python project configuration & dependencies
├── uv.lock            # Locked dependency versions
├── README.md          # User-facing documentation
├── LICENSE            # MIT License
├── .gitignore         # Standard Python gitignore
└── CLAUDE.md          # This file - AI assistant guide
```

**Notable**: This is a single-file implementation. All server logic is contained in `btt_mcp.py` (~1,366 lines).

## Code Architecture

### File Organization

`btt_mcp.py` is structured in clear sections (in order):

1. **Configuration Constants** (lines 27-51)
   - BTT connection defaults (host, port, socket path)
   - Trigger type mappings
   - Named trigger constants

2. **Pydantic Input Models** (lines 57-497)
   - One model per tool
   - All use `ConfigDict(str_strip_whitespace=True, extra='forbid')`
   - Standard pattern: params + `connection: BTTConnectionConfig`

3. **HTTP Client Utilities** (lines 500-572)
   - `_build_url()` - Construct BTT API URLs with params
   - `_http_request()` - Async HTTP requests via httpx
   - `_cli_request()` - Subprocess calls to bttcli
   - `_btt_request()` - Router between HTTP/CLI modes

4. **Formatting Utilities** (lines 575-653)
   - `_format_trigger()` - Convert BTT trigger JSON to markdown
   - `_format_triggers_list()` - Format multiple triggers
   - `_format_preset_details()` - Format preset info

5. **MCP Tool Implementations** (lines 656-1353)
   - 20 `@mcp.tool()` decorated functions
   - Each has consistent structure and annotations

6. **Server Entry Point** (lines 1356-1365)
   - `main()` function that calls `mcp.run()`

### Key Design Patterns

#### 1. Input Validation Pattern
Every tool uses Pydantic models for input validation:
```python
class SomeToolInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    param_name: str = Field(
        ...,  # Required
        description="Shown to AI and users",
        min_length=1  # Constraints as needed
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )
```

**Important**: The `extra='forbid'` prevents unknown parameters, helping catch typos.

#### 2. Tool Decorator Pattern
All tools use consistent MCP annotations:
```python
@mcp.tool(
    name="btt_tool_name",
    annotations={
        "title": "Human Readable Title",
        "readOnlyHint": True/False,      # Does it modify state?
        "destructiveHint": True/False,    # Is it dangerous?
        "idempotentHint": True/False,     # Same result on repeat?
        "openWorldHint": True/False       # Can affect external systems?
    }
)
async def btt_tool_name(params: ToolInput) -> str:
    """Docstring shown to AI and users."""
    # Implementation
```

**Annotations Guide**:
- `readOnlyHint: True` - Read-only operations (get_triggers, get_variable)
- `destructiveHint: True` - ONLY for `btt_delete_trigger` (permanent deletion)
- `idempotentHint: True` - Operations that are safe to repeat (set_variable, update_widget)
- `openWorldHint: True` - Can affect systems outside BTT (trigger_named, display_notification)

#### 3. Response Format Pattern
Tools that return data support dual output modes:
```python
if params.response_format == ResponseFormat.JSON:
    return result  # Raw JSON string from BTT

# Otherwise format as markdown
data = json.loads(result)
return _format_something(data)
```

#### 4. Error Handling Pattern
All BTT requests check for errors early:
```python
result = await _btt_request(endpoint, params, config)

if result.startswith("Error:"):
    return result  # Return error message to user

# Continue with success path
```

Errors are prefixed with `"Error:"` for easy detection.

### BTT Communication Modes

The server supports **two communication methods** with BetterTouchTool:

#### HTTP Mode (Default)
- Uses `httpx` to call BTT's webserver API
- Default: `http://127.0.0.1:12345/endpoint/?params`
- Supports shared secret authentication
- More compatible, easier to debug

#### CLI Mode (Optional)
- Uses `bttcli` command-line tool via subprocess
- Communicates via Unix socket: `/tmp/com.hegenberg.BetterTouchTool.sock`
- Faster (lower latency)
- Requires BTT to be installed in standard location

**Selection**: Controlled by `connection.use_cli` parameter in each tool call.

## Tool Categories

### 1. Configuration Reading (Read-Only)
- `btt_get_triggers` - Filter and retrieve triggers (by type, app, parent)
- `btt_get_trigger` - Get single trigger by UUID
- `btt_list_named_triggers` - List all named triggers (trigger_id=643)
- `btt_get_preset_details` - Get preset info and status

**Use When**: Understanding existing BTT configuration, exploring setup

### 2. Trigger Management (Modifying)
- `btt_trigger_named` - Execute named trigger by name
- `btt_trigger_action` - Execute arbitrary BTT action from JSON
- `btt_execute_trigger` - Run all actions for a trigger UUID
- `btt_add_trigger` - Create new trigger from JSON
- `btt_update_trigger` - Modify existing trigger
- `btt_delete_trigger` - **DESTRUCTIVE** - Permanently remove trigger

**Use When**: Executing automations, creating/modifying triggers

### 3. Variable Management
- `btt_get_variable` - Read string/number variables
- `btt_set_variable` - Write variables (persistent or runtime)

**Use When**: Dynamic workflows, storing state, reading system info

### 4. Widget Control
- `btt_update_widget` - Update Touch Bar/Menubar/Stream Deck widget appearance
- `btt_refresh_widget` - Re-run scripts for a widget

**Use When**: Updating displays, showing status information

### 5. Clipboard Operations
- `btt_get_clipboard` - Read clipboard (various formats, optional base64)
- `btt_set_clipboard` - Write to clipboard

**Use When**: Text processing, data transfer workflows

### 6. Preset Management
- `btt_export_preset` - Save preset to file (backup/sharing)
- `btt_import_preset` - Load preset from file

**Use When**: Backup, migration, configuration sharing

### 7. System Utilities
- `btt_display_notification` - Show macOS notification
- `btt_reveal_in_ui` - Open BTT and navigate to element

**Use When**: User feedback, debugging, navigation

## Development Conventions

### Code Style
- **Type hints**: Used throughout for function signatures
- **Docstrings**: Required for all MCP tools (shows in AI context)
- **Async**: All tool functions are `async def` (required by FastMCP)
- **Private functions**: Prefix with `_` (e.g., `_format_trigger`, `_btt_request`)

### Naming Conventions
- **Tool names**: `btt_verb_noun` pattern (e.g., `btt_get_triggers`, `btt_set_variable`)
- **Input models**: `VerbNounInput` pattern (e.g., `GetTriggersInput`, `SetVariableInput`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_BTT_PORT`, `NAMED_TRIGGER_ID`)

### Parameter Patterns
- **UUIDs**: Always validate with `min_length=36, max_length=36`
- **Optional strings**: Use `Optional[str] = Field(default=None, ...)`
- **Booleans**: Always provide default value
- **Enums**: Use for fixed sets (e.g., `ResponseFormat`, though more could be used)

### Error Messages
Format: `"Error: <specific issue>. <helpful context or fix>."`

Examples:
- `"Error: Could not connect to BTT webserver at {host}:{port}. Is the webserver enabled in BTT preferences?"`
- `"Error: Authentication failed. Check your shared_secret configuration."`
- `"Error: bttcli not found. Make sure BetterTouchTool is installed."`

## BTT-Specific Knowledge

### Trigger Types
BTT uses internal type names (see `TRIGGER_TYPES` constant):
- `BTTTriggerTypeKeyboardShortcut` - Keyboard shortcuts
- `BTTTriggerTypeTouchBar` - Touch Bar widgets
- `BTTTriggerTypeOther` - Named triggers (actually uses `trigger_id=643`)
- `BTTTriggerTypeStreamDeck` - Stream Deck buttons
- Many more...

### Named Triggers
- **Identifier**: `trigger_id = 643`
- **Purpose**: Reusable actions callable by name
- **Access**: Use `btt_list_named_triggers` or `btt_get_triggers` with `trigger_id=643`

### UUIDs
- All BTT elements (triggers, widgets, presets) have UUIDs
- UUIDs are 36 characters (standard UUID format with hyphens)
- Used for precise identification and modification

### JSON Formats
BTT uses JSON extensively:
- **Trigger JSON**: Copy from BTT via right-click → "Copy JSON"
- **Action JSON**: Similar, for individual actions
- **Update JSON**: Partial object with fields to change

## Common Modification Patterns

### Adding a New Tool

1. **Create Input Model** (in Pydantic section):
```python
class NewToolInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    param1: str = Field(..., description="What this param does")
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )
```

2. **Implement Tool** (in MCP Tools section):
```python
@mcp.tool(
    name="btt_new_tool",
    annotations={
        "title": "New Tool",
        "readOnlyHint": True,  # Adjust as needed
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_new_tool(params: NewToolInput) -> str:
    """Clear description of what this tool does."""
    result = await _btt_request('btt_endpoint', {'param': params.param1}, params.connection)

    if result.startswith("Error:"):
        return result

    return f"Success: {result}"
```

3. **Update README.md** (add to appropriate table)

### Adding a Response Format
Some tools support `response_format` (markdown vs JSON). To add this to a tool:

1. Add to input model:
```python
response_format: ResponseFormat = Field(
    default=ResponseFormat.MARKDOWN,
    description="Output format: 'markdown' for human-readable or 'json' for raw data"
)
```

2. Add format handling in tool:
```python
if params.response_format == ResponseFormat.JSON:
    return result

# Parse and format
data = json.loads(result)
return _format_something(data)
```

3. Create formatter function if needed (in Formatting Utilities section)

### Adding a Connection Option
New connection parameters go in `BTTConnectionConfig`:

```python
class BTTConnectionConfig(BaseModel):
    # ... existing fields ...
    new_option: bool = Field(
        default=False,
        description="Description of what this enables"
    )
```

Then use in `_http_request`, `_cli_request`, or `_btt_request` as appropriate.

## Testing and Validation

### Manual Testing
```bash
# Run server directly (for debugging)
uv run btt_mcp.py

# Or with standard Python
python btt_mcp.py
```

### MCP Inspector
The official MCP debugging tool:
```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/bettertouchtool-mcp-server run btt_mcp.py
```

This provides a web UI to test tools interactively.

### Prerequisites for Testing
1. **BetterTouchTool running** on macOS
2. **Webserver enabled**: Preferences → Advanced → Webserver
3. **Port accessible**: Default 12345 (or configured port)
4. **Shared secret** (if configured): Must match in tool calls

### Common Test Scenarios
1. **Connection**: Try `btt_get_triggers` with no filters
2. **Named triggers**: Use `btt_list_named_triggers`
3. **Variable access**: `btt_get_variable` with a known variable
4. **Trigger execution**: `btt_trigger_named` with safe trigger

## Installation and Deployment

### For Development
```bash
# Clone repository
git clone <repo-url>
cd bettertouchtool-mcp-server

# Install with uv (creates .venv automatically)
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### For Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bettertouchtool": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/bettertouchtool-mcp-server",
        "run",
        "btt_mcp.py"
      ]
    }
  }
}
```

**Important**: Use absolute paths, restart Claude Desktop after changes.

## Important Considerations for AI Assistants

### 1. UUID Handling
- Always validate UUIDs are 36 characters before using
- Don't generate random UUIDs - get them from BTT via `btt_get_triggers`
- UUIDs are case-sensitive

### 2. Destructive Operations
- **ONLY `btt_delete_trigger` is marked destructive** - confirm with user first
- Modifications (update, add) are not destructive but should be confirmed for user's config
- Always explain what will change before executing

### 3. Connection Configuration
- Default HTTP connection works for most users
- CLI mode is faster but requires BTT in standard location
- Shared secrets must match between BTT and tool calls

### 4. Error Handling
- All errors start with `"Error:"` prefix
- Common errors:
  - Connection refused → BTT not running or webserver disabled
  - 403 Forbidden → Shared secret mismatch
  - bttcli not found → BTT not in standard location (CLI mode)

### 5. Response Formats
- Use markdown format for user-facing responses (easier to read)
- Use JSON format when you need to parse and manipulate data
- Not all tools support both formats (check input model)

### 6. Trigger Filters
When using `btt_get_triggers`:
- **No filters** = All triggers (can be large!)
- **Filter by app** = Triggers for specific application
- **Filter by type** = e.g., only keyboard shortcuts
- **Filter by parent_uuid** = Triggers in a specific folder/group

### 7. Named Triggers vs Regular Triggers
- **Named triggers**: Callable by name, use `btt_trigger_named`
- **Regular triggers**: Bound to specific inputs (keys, gestures, etc.)
- Both can execute actions, but named triggers are designed for programmatic access

### 8. Variables
- BTT has built-in variables (e.g., `BTTActiveAppBundleIdentifier`)
- User variables can be created dynamically via `btt_set_variable`
- **Persistent variables** survive BTT restarts, runtime variables don't

### 9. Widgets
- UUIDs identify widgets across Touch Bar, Menubar, Stream Deck
- Updates are temporary unless you also update the underlying configuration
- Use `refresh_widget` for script-based widgets to re-run their scripts

### 10. Best Practices for Modifications
1. **Read first**: Use `btt_get_trigger` before modifying
2. **Small changes**: Update specific fields rather than replacing entire configurations
3. **Test safely**: Try on non-critical triggers first
4. **Backup**: Suggest `btt_export_preset` before major changes
5. **Verify**: Check results with `btt_get_trigger` after modifications

## Common User Workflows

### Exploring Configuration
1. List all named triggers: `btt_list_named_triggers`
2. Find app-specific triggers: `btt_get_triggers` with `app_bundle_identifier`
3. Get details: `btt_get_trigger` with UUID from above

### Executing Automation
1. Find trigger name: `btt_list_named_triggers`
2. Execute: `btt_trigger_named` with the name
3. Or directly execute by UUID: `btt_execute_trigger`

### Creating New Trigger
1. Get example: `btt_get_trigger` for similar existing trigger
2. Modify JSON (change name, UUID, actions)
3. Add: `btt_add_trigger` with modified JSON

### Managing Variables
1. Read current value: `btt_get_variable`
2. Update: `btt_set_variable` (choose persistent if needed)
3. Use in triggers (BTT can reference variables in actions)

### Widget Updates
1. Find widget UUID: `btt_get_triggers` filtered by type
2. Update appearance: `btt_update_widget` with new text/colors
3. For script widgets: `btt_refresh_widget` to re-run

## Dependencies

Defined in `pyproject.toml`:
- **httpx** (>=0.28.1): Async HTTP client for BTT API calls
- **mcp** (>=1.22.0): Model Context Protocol SDK (via FastMCP)
- **pydantic** (>=2.12.5): Data validation and settings management

**Python requirement**: >=3.12 (uses modern type hints and async features)

## Git Development Workflow

When making changes:

1. **Branch naming**: Use descriptive names (e.g., `feature/add-new-tool`, `fix/error-handling`)
2. **Commit messages**: Clear, descriptive (e.g., "Add clipboard format validation", "Fix UUID length check")
3. **Testing**: Test with MCP Inspector before committing
4. **Documentation**: Update README.md if adding/changing tools

## Platform Constraints

- **macOS only**: BetterTouchTool is macOS-exclusive
- **BTT required**: Must have valid BTT license and running instance
- **Python 3.12+**: Uses modern Python features
- **No Windows/Linux**: Not cross-platform compatible

## File Locations to Remember

- **BTT webserver config**: BetterTouchTool → Preferences → Advanced → Webserver
- **bttcli**: `/Applications/BetterTouchTool.app/Contents/SharedSupport/bin/bttcli`
- **Unix socket**: `/tmp/com.hegenberg.BetterTouchTool.sock`
- **Claude config**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Default port**: 12345

## Key Reference Links

- **MCP Documentation**: https://modelcontextprotocol.io
- **BTT API Docs**: https://docs.folivora.ai/docs/1104_webserver.html
- **FastMCP**: https://github.com/jlowin/fastmcp
- **Pydantic**: https://docs.pydantic.dev

---

## Quick Reference: Adding a Feature

1. ✅ Determine if it's a new tool or enhancement to existing tool
2. ✅ Check BTT API documentation for endpoint and parameters
3. ✅ Add/modify Pydantic input model
4. ✅ Implement tool function with proper annotations
5. ✅ Add error handling (check for "Error:" prefix)
6. ✅ Test with MCP Inspector
7. ✅ Update README.md documentation
8. ✅ Commit with clear message

## Quick Reference: Debugging Issues

| Issue | Check |
|-------|-------|
| "Connection refused" | BTT running? Webserver enabled? Correct port? |
| "403 Forbidden" | Shared secret matches? |
| "bttcli not found" | BTT installed in standard location? CLI mode needed? |
| Tool not appearing | Claude Desktop restarted? Config JSON valid? |
| Empty response | Normal for some operations (trigger execution, updates) |
| JSON parse error | BTT returned error message, not JSON |

---

*This document is maintained for AI assistants working with this codebase. Keep it updated when making structural changes.*
