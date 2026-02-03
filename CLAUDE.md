# BetterTouchTool MCP Server

An MCP (Model Context Protocol) server for controlling and managing BetterTouchTool on macOS.

## Project Structure

```
bettertouchtool-mcp-server/
├── src/
│   └── btt_mcp/
│       ├── __init__.py           # Package init, exports main()
│       ├── server.py             # FastMCP server initialization
│       ├── config.py             # Constants, config file loading (YAML)
│       ├── models/               # Pydantic input models
│       │   ├── __init__.py       # Exports all models
│       │   ├── common.py         # ResponseFormat, BTTConnectionConfig
│       │   ├── triggers.py       # Trigger CRUD models
│       │   ├── actions.py        # Action triggering models
│       │   ├── variables.py      # Variable get/set models
│       │   ├── widgets.py        # Widget update models
│       │   ├── clipboard.py      # Clipboard models
│       │   └── presets.py        # Preset/notification models
│       ├── client/               # BTT communication layer
│       │   ├── __init__.py       # Exports btt_request
│       │   ├── base.py           # Request dispatcher
│       │   ├── http.py           # HTTP client (webserver)
│       │   └── cli.py            # CLI client (bttcli)
│       ├── formatters/           # Output formatting
│       │   ├── __init__.py
│       │   └── markdown.py       # Markdown formatters
│       └── tools/                # MCP tool implementations
│           ├── __init__.py       # Imports all tool modules
│           ├── triggers.py       # Trigger management tools
│           ├── actions.py        # Action execution tools
│           ├── variables.py      # Variable tools
│           ├── widgets.py        # Widget tools
│           ├── clipboard.py      # Clipboard tools
│           └── presets.py        # Preset/notification/UI tools
├── tests/
│   ├── test_models.py            # Model validation tests
│   ├── test_client.py            # Client/URL building tests
│   ├── test_formatters.py        # Formatter output tests
│   ├── test_imports.py           # Import and structure tests
│   └── examples/
│       └── example_settings.btt-preset
├── btt_mcp.py                    # Legacy single-file (deprecated)
├── pyproject.toml
├── README.md
└── CLAUDE.md                     # This file
```

## Architecture

### Dependency Flow

```
server.py (FastMCP instance)
    ↓
tools/* (register @mcp.tool decorators)
    ↓
├── models/* (Pydantic input validation)
├── client/* (BTT communication)
└── formatters/* (output formatting)
    ↓
config.py (constants)
```

### Key Design Decisions

1. **Lazy tool registration**: Tools are imported in `main()` to avoid circular imports
2. **Shared MCP instance**: `server.py` exports `mcp` which all tool modules import
3. **Two communication methods**: HTTP (webserver) and CLI (bttcli via Unix socket)
4. **Pydantic models**: All tool inputs use Pydantic for validation and documentation

## Development

### Running the Server

```bash
# Install in development mode
uv pip install -e .

# Run the server
btt-mcp-server

# Or directly
python -m btt_mcp
```

### Adding a New Tool

1. **Create or choose a tool module** in `src/btt_mcp/tools/`

2. **Add input model** in appropriate `models/` file:

   ```python
   # models/my_feature.py
   class MyNewInput(BaseModel):
       param: str = Field(..., description="Parameter description")
       connection: BTTConnectionConfig = Field(default_factory=BTTConnectionConfig)
   ```

3. **Implement the tool**:

   ```python
   # tools/my_feature.py
   from btt_mcp.server import mcp
   from btt_mcp.client import btt_request
   from btt_mcp.models import MyNewInput

   @mcp.tool(
       name="btt_my_tool",
       annotations={
           "title": "My Tool Title",
           "readOnlyHint": True,
           "destructiveHint": False,
           "idempotentHint": True,
           "openWorldHint": False,
       },
   )
   async def btt_my_tool(params: MyNewInput) -> str:
       """Tool docstring becomes the MCP description."""
       result = await btt_request("btt_endpoint", {...}, params.connection)
       return result
   ```

4. **Export from `models/__init__.py`** and **import in `tools/__init__.py`**

### Adding a New BTT Endpoint

1. Add any new constants to `config.py`
2. The client layer (`client/base.py`) handles dispatching to HTTP or CLI
3. Add formatters to `formatters/markdown.py` if needed

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_models.py

# Run with coverage
uv run pytest --cov=btt_mcp
```

**Test Structure:**

| File | Tests | Coverage |
|------|-------|----------|
| `test_models.py` | 17 | Pydantic validation, defaults, required fields |
| `test_client.py` | 8 | URL building, config constants |
| `test_formatters.py` | 12 | Markdown output formatting |
| `test_imports.py` | 8 | Module imports, tool registration |

## BTT Communication

### Configuration File

Connection settings are loaded from `~/.config/btt-mcp/config.yml`:

```yaml
host: 127.0.0.1
port: 56786
shared_secret: null  # Set if BTT has shared secret configured
use_cli: false       # Use bttcli instead of HTTP
```

The file is optional — defaults are used if it doesn't exist. See `config.py` for:

- `_load_config_file()` - YAML loading with error handling
- `get_default_*()` - Functions that read config or return defaults
- `create_default_config()` - Creates config file with defaults

### HTTP Webserver (default)

- Requires BTT webserver enabled in preferences
- Port configurable (default: 56786)
- Optional shared secret authentication

### CLI (bttcli)

- Uses Unix socket (`/tmp/com.hegenberg.BetterTouchTool.sock`)
- Generally faster than HTTP
- Set `use_cli: true` in connection config

## Tool Categories

| Category | Module | Tools |
|----------|--------|-------|
| **Triggers** | `triggers.py` | get_triggers, get_trigger, list_named_triggers, add_trigger, update_trigger, delete_trigger, execute_trigger |
| **Actions** | `actions.py` | trigger_named, trigger_action |
| **Variables** | `variables.py` | get_variable, set_variable |
| **Widgets** | `widgets.py` | update_widget, refresh_widget |
| **Clipboard** | `clipboard.py` | get_clipboard, set_clipboard |
| **Presets** | `presets.py` | export_preset, import_preset, get_preset_details, display_notification, reveal_in_ui |

## Extension Points

### Adding New Widget Types

1. Add endpoint mapping to `WIDGET_ENDPOINT_MAP` in `config.py`
2. Update `UpdateWidgetInput.widget_type` description
3. The existing `btt_update_widget` tool will work automatically

### Adding New Trigger Types

1. Add to `TRIGGER_TYPES` dict in `config.py`
2. Consider adding specialized formatters if the trigger has unique properties

### Custom Formatters

Create new formatters in `formatters/` for specialized output:

```python
# formatters/json_export.py
def format_for_export(data: dict) -> str:
    """Format trigger data for re-import."""
    ...
```

## Common Patterns

### Error Handling

All tools check for error responses:

```python
if result.startswith("Error:"):
    return result
```

### Response Formatting

Tools with `response_format` parameter support both JSON and Markdown:

```python
if params.response_format == ResponseFormat.JSON:
    return result

try:
    data = json.loads(result)
    return format_triggers_list(data)
except json.JSONDecodeError:
    return f"Error parsing response: {result}"
```

### Empty Response Handling

BTT often returns empty strings on success:

```python
if not result or result.strip() == "":
    return "Operation completed successfully."
```

## Migration from Single File

The original `btt_mcp.py` (1366 lines) has been refactored into this modular structure. The old file is kept for backwards compatibility but is deprecated.

Key changes:

- All imports now come from `btt_mcp.*` submodules
- Entry point is `btt_mcp:main` (same as before)
- Tool behavior is identical
