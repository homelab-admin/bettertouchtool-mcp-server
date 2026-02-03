# BetterTouchTool MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that enables AI assistants like Claude to control and interact with [BetterTouchTool](https://folivora.ai/) on macOS.

## What is this?

This MCP server acts as a bridge between Claude (or other MCP-compatible AI assistants) and BetterTouchTool, allowing you to:

- **Query your BTT configuration** - Understand what triggers, shortcuts, and automations you have set up
- **Execute triggers and actions** - Run named triggers, keyboard shortcuts, or any BTT action
- **Manage variables** - Get and set BTT variables for dynamic workflows
- **Update widgets** - Modify Touch Bar, Menu Bar, or Stream Deck widgets in real-time
- **Control presets** - Export, import, and manage BTT presets
- **Access clipboard** - Read and write clipboard contents programmatically

## Prerequisites

- **macOS** (BetterTouchTool is macOS-only)
- **BetterTouchTool** installed with a valid license
- **Python 3.12+**
- **uv** (recommended) or pip for package management
- **Claude Desktop** or another MCP-compatible client

## Installation

### 1. Enable BTT Webserver

First, enable the BetterTouchTool webserver:

1. Open BetterTouchTool
2. Go to **Preferences** → **Advanced** → **Webserver**
3. Check **Enable Webserver**
4. Note the port (default: `56786`)
5. Optionally set a **Shared Secret** for authentication

### 2. Install the MCP Server

#### Option A: Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/bettertouchtool-mcp-server.git
cd bettertouchtool-mcp-server

# Install dependencies with uv
uv sync
```

#### Option B: Install with pip

```bash
# Clone the repository
git clone https://github.com/your-username/bettertouchtool-mcp-server.git
cd bettertouchtool-mcp-server

# Create virtual environment and install
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Configure Claude Desktop

Add the server to your Claude Desktop configuration file:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Using uv:

```json
{
  "mcpServers": {
    "bettertouchtool": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/bettertouchtool-mcp-server",
        "run",
        "btt-mcp-server"
      ]
    }
  }
}
```

#### Using Python directly:

```json
{
  "mcpServers": {
    "bettertouchtool": {
      "command": "/path/to/bettertouchtool-mcp-server/.venv/bin/python",
      "args": ["-m", "btt_mcp"]
    }
  }
}
```

### 4. Restart Claude Desktop

After saving the configuration, restart Claude Desktop to load the MCP server.

## Available Tools

The server provides 20 tools organized into categories:

### Configuration Reading

| Tool | Description |
|------|-------------|
| `btt_get_triggers` | List triggers with optional filtering by type, app, or parent |
| `btt_get_trigger` | Get detailed info about a specific trigger by UUID |
| `btt_list_named_triggers` | List all named triggers (quick actions) |
| `btt_get_preset_details` | Get info about presets and their status |

### Trigger Management

| Tool | Description |
|------|-------------|
| `btt_trigger_named` | Execute a named trigger by name |
| `btt_trigger_action` | Execute any BTT action via JSON definition |
| `btt_execute_trigger` | Execute all actions assigned to a trigger UUID |
| `btt_add_trigger` | Create a new trigger from JSON definition |
| `btt_update_trigger` | Modify an existing trigger |
| `btt_delete_trigger` | Remove a trigger (⚠️ destructive) |

### Variable Management

| Tool | Description |
|------|-------------|
| `btt_get_variable` | Read string or number variables |
| `btt_set_variable` | Set persistent or runtime variables |

### Widget Control

| Tool | Description |
|------|-------------|
| `btt_update_widget` | Update widget text, icon, or colors |
| `btt_refresh_widget` | Force a script widget to refresh |

### Clipboard Operations

| Tool | Description |
|------|-------------|
| `btt_get_clipboard` | Read clipboard in various formats |
| `btt_set_clipboard` | Write to clipboard |

### Preset Management

| Tool | Description |
|------|-------------|
| `btt_export_preset` | Export preset to a file |
| `btt_import_preset` | Import preset from a file |

### System Utilities

| Tool | Description |
|------|-------------|
| `btt_display_notification` | Show a macOS notification |
| `btt_reveal_in_ui` | Open BTT and navigate to an element |

## Usage Examples

### Exploring Your Configuration

Ask Claude:

> "What triggers do I have set up in BetterTouchTool?"

> "Show me all my named triggers"

> "What keyboard shortcuts do I have configured?"

### Running Automations

> "Run my 'Toggle Dark Mode' trigger in BTT"

> "Execute the BTT trigger that opens my development environment"

### Working with Variables

> "What's the current value of my 'workMode' variable in BTT?"

> "Set my BTT variable 'currentProject' to 'MCP Server Development'"

### Updating Widgets

> "Update my Touch Bar clock widget to show 'Meeting in 5 min' with a red background"

> "Refresh my system stats widget"

### Managing Configuration

> "Export my current BTT preset to ~/Desktop/my-preset.bttpreset"

> "Show me the details of trigger with UUID abc-123-def"

### Complex Workflows

> "I want to create a new named trigger that opens Safari and navigates to my project management tool"

> "Help me understand what my 'Morning Routine' trigger does and suggest improvements"

## Configuration

Configuration is stored in `~/.config/btt-mcp/config.yml`. The file is created automatically with defaults on first use, or you can create it manually:

```yaml
# BTT MCP Server Configuration
host: 127.0.0.1
port: 56786
shared_secret: null  # Set this if you've configured a shared secret in BTT
use_cli: false       # Set to true to use bttcli instead of HTTP
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `host` | `127.0.0.1` | BTT webserver host |
| `port` | `56786` | BTT webserver port |
| `shared_secret` | `null` | Shared secret for authentication (if configured in BTT) |
| `use_cli` | `false` | Use `bttcli` CLI tool instead of HTTP (faster, uses Unix socket) |

### Example: With Shared Secret

If you've configured a shared secret in BTT preferences:

```yaml
host: 127.0.0.1
port: 56786
shared_secret: my_secret_key
```

### Example: Using CLI Mode

For faster performance using the Unix socket:

```yaml
use_cli: true
```

This uses the socket at `/tmp/com.hegenberg.BetterTouchTool.sock` for lower latency.

## Trigger Types

When filtering triggers, you can use these types:

- `named_trigger` - Named triggers (quick actions)
- `keyboard_shortcut` - Keyboard shortcuts
- `touchbar` - Touch Bar items
- `trackpad` - Trackpad gestures
- `magic_mouse` - Magic Mouse gestures
- `drawings` - Drawing gestures
- `siri_remote` - Siri Remote
- `normal_mouse` - Regular mouse buttons
- `stream_deck` - Stream Deck buttons
- `midi` - MIDI triggers
- `menubar` - Menu bar items

## Troubleshooting

### "Connection refused" errors

1. Ensure BTT is running
2. Verify webserver is enabled in BTT preferences
3. Check the port matches (default: 12345)

### "403 Forbidden" errors

You have a shared secret configured in BTT. Either:

- Add `shared_secret: your_secret` to `~/.config/btt-mcp/config.yml`
- Remove the shared secret from BTT preferences

### "bttcli not found" (CLI mode)

The CLI tool should be at:
- `/Applications/BetterTouchTool.app/Contents/SharedSupport/bin/bttcli`
- or `~/Applications/BetterTouchTool.app/Contents/SharedSupport/bin/bttcli`

### Tools not appearing in Claude

1. Check Claude Desktop config syntax is valid JSON
2. Verify the path to the MCP server is correct
3. Restart Claude Desktop
4. Check Console.app for MCP-related errors

## Development

### Project Structure

The codebase is organized into a modular package:

```
src/btt_mcp/
├── server.py      # FastMCP server initialization
├── config.py      # Constants and configuration
├── models/        # Pydantic input models (7 files)
├── client/        # BTT communication (HTTP + CLI)
├── formatters/    # Output formatting
└── tools/         # MCP tool implementations (6 files)
```

See [CLAUDE.md](CLAUDE.md) for detailed architecture documentation.

### Running locally for testing

```bash
# With uv
uv run btt-mcp-server

# Or directly
python -m btt_mcp
```

### Running Tests

```bash
# Run all 48 tests
uv run pytest

# With verbose output
uv run pytest -v
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/project run btt-mcp-server
```

## API Reference

This server implements the [BTT Webserver API](https://docs.folivora.ai/docs/1104_webserver.html). Key endpoints used:

- `GET /get_triggers` - Retrieve trigger configurations
- `GET /trigger_named` - Execute named triggers
- `GET /trigger_action` - Execute arbitrary actions
- `GET /get_string_variable` / `set_string_variable` - Variable management
- `GET /update_touch_bar_widget` - Widget updates
- `GET /get_clipboard_content` / `set_clipboard_content` - Clipboard access

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- [BetterTouchTool](https://folivora.ai/) by folivora.AI
- [Model Context Protocol](https://modelcontextprotocol.io) by Anthropic
- [FastMCP](https://github.com/jlowin/fastmcp) for the Python MCP framework
