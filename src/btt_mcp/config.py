"""
Configuration constants and connection settings for BTT MCP Server.
"""

import os
from pathlib import Path
from typing import Any

import yaml

# =============================================================================
# Config File Path
# =============================================================================

CONFIG_DIR = Path.home() / ".config" / "btt-mcp"
CONFIG_FILE = CONFIG_DIR / "config.yml"

# =============================================================================
# Connection Constants (defaults, can be overridden by config file)
# =============================================================================

DEFAULT_BTT_PORT = 56786
DEFAULT_BTT_HOST = "127.0.0.1"
DEFAULT_SHARED_SECRET: str | None = None
DEFAULT_USE_CLI = False
BTT_SOCKET_PATH = "/tmp/com.hegenberg.BetterTouchTool.sock"


def _load_config_file() -> dict[str, Any]:
    """Load configuration from YAML file if it exists.

    Returns:
        Configuration dictionary, empty if file doesn't exist.
    """
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f)
            return config if isinstance(config, dict) else {}
    except (yaml.YAMLError, OSError):
        return {}


def _get_config_value(key: str, default: Any) -> Any:
    """Get a configuration value from file or return default.

    Args:
        key: Configuration key (supports nested keys with dots, e.g., 'connection.host')
        default: Default value if not found in config

    Returns:
        Configuration value or default
    """
    config = _load_config_file()

    # Support nested keys like 'connection.host'
    keys = key.split(".")
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value


def get_default_host() -> str:
    """Get the default BTT host from config file or fallback."""
    return _get_config_value("host", DEFAULT_BTT_HOST)


def get_default_port() -> int:
    """Get the default BTT port from config file or fallback."""
    return _get_config_value("port", DEFAULT_BTT_PORT)


def get_default_shared_secret() -> str | None:
    """Get the default shared secret from config file or fallback."""
    return _get_config_value("shared_secret", DEFAULT_SHARED_SECRET)


def get_default_use_cli() -> bool:
    """Get whether to use CLI by default from config file or fallback."""
    return _get_config_value("use_cli", DEFAULT_USE_CLI)


def ensure_config_dir() -> Path:
    """Ensure the config directory exists and return the config file path.

    Returns:
        Path to the config file (may not exist yet)
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_FILE


def create_default_config() -> Path:
    """Create a default config file if it doesn't exist.

    Returns:
        Path to the config file
    """
    config_path = ensure_config_dir()

    if not config_path.exists():
        default_config = {
            "host": DEFAULT_BTT_HOST,
            "port": DEFAULT_BTT_PORT,
            "shared_secret": None,
            "use_cli": False,
        }
        with open(config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

    return config_path

# CLI paths (checked in order)
BTTCLI_PATHS = [
    "/Applications/BetterTouchTool.app/Contents/SharedSupport/bin/bttcli",
    os.path.expanduser("~/Applications/BetterTouchTool.app/Contents/SharedSupport/bin/bttcli"),
]

# =============================================================================
# Trigger Type Constants
# =============================================================================

# Common trigger types for reference and validation
TRIGGER_TYPES = {
    "keyboard_shortcut": "BTTTriggerTypeKeyboardShortcut",
    "trackpad": "BTTTriggerTypeTrackpad",
    "magic_mouse": "BTTTriggerTypeMagicMouse",
    "touch_bar": "BTTTriggerTypeTouchBar",
    "siri_remote": "BTTTriggerTypeSiriRemote",
    "named": "BTTTriggerTypeOther",
    "stream_deck": "BTTTriggerTypeStreamDeck",
    "floating_menu": "BTTTriggerTypeFloatingMenu",
    "notch_bar": "BTTTriggerTypeNotchBar",
    "drawing": "BTTTriggerTypeDrawing",
}

# Reverse mapping for display purposes
TRIGGER_TYPE_NAMES = {v: k for k, v in TRIGGER_TYPES.items()}

# Named triggers have this specific trigger_id
NAMED_TRIGGER_ID = 643

# =============================================================================
# Widget Type Mappings
# =============================================================================

WIDGET_ENDPOINT_MAP = {
    "touch_bar": "update_touch_bar_widget",
    "menubar": "update_menubar_item",
    "stream_deck": "update_stream_deck_widget",
}


def get_bttcli_path() -> str | None:
    """Find the bttcli executable path."""
    for path in BTTCLI_PATHS:
        if os.path.exists(path):
            return path
    return None
