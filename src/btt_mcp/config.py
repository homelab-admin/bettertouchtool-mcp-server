"""
Configuration constants and connection settings for BTT MCP Server.
"""

import os

# =============================================================================
# Connection Constants
# =============================================================================

DEFAULT_BTT_PORT = 12345
DEFAULT_BTT_HOST = "127.0.0.1"
BTT_SOCKET_PATH = "/tmp/com.hegenberg.BetterTouchTool.sock"

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
