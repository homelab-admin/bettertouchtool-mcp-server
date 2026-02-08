"""
Floating menu models for BetterTouchTool.

Based on BTT Floating Menu JSON documentation:
https://docs.folivora.ai/docs/2001_floating_menu_json.html

Note: In BTT JSON, special prefixes are used:
- BTT = © (used for trigger properties)
- BTTMenu = $ (used for menu config properties)
- BTTMenuItem = § (used for menu item properties)
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.models.common import BTTConnectionConfig, ResponseFormat

# =============================================================================
# Floating Menu Constants
#
# These are plain int constants instead of IntEnum to avoid $ref in JSON schema.
# VS Code Copilot cannot resolve $ref references in tool parameter schemas.
# See: https://github.com/microsoft/vscode/issues/286179
# =============================================================================


# Trigger types for floating menu elements
class FloatingMenuTriggerType:
    MENU = 767  # Top-level floating menu
    STANDARD_ITEM = 773  # Button with actions
    SUBMENU = 774  # Contains nested items
    SLIDER = 775
    TEXT_FIELD = 776  # Value queryable via scripts
    BACK_BUTTON = 777  # For submenus
    WEBVIEW = 778  # Displays HTML from BTTMenuItemText
    TRACKPAD_WIDGET = 800
    ROW_BREAKER = 801
    COLUMN_BREAKER = 802
    TEXT_AREA = 810  # Value queryable via scripts
    FLOATING_MENU_REFERENCE = 811


# Menu positioning types
class PositioningType:
    FREE_MOVE = 0
    FIXED_POSITION = 1
    MENUBAR_STATUS_ITEM = 2


# What to position the menu relative to
class PositionRelativeTo:
    FOCUSED_WINDOW = 0
    SCREEN_WITH_MOUSE = 1
    FOCUSED_SCREEN = 3
    MOUSE_POSITION = 7
    BUILTIN = 8
    NOTCH = 11
    FOCUSED_MENUBAR = 12
    SCREEN_WITH_DOCK = 19
    GREEN_WINDOW_BUTTON = 20
    HOVERED_FLOATING_MENU_ITEM = 21
    SPECIFIC_FLOATING_MENU = 22
    DOCK = 23


# Anchor positions for menu and relation
class AnchorPosition:
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3
    CENTER = 4
    TOP_EDGE_CENTER = 5
    RIGHT_EDGE_CENTER = 6
    BOTTOM_EDGE_CENTER = 7
    LEFT_EDGE_CENTER = 8


# Menu layout direction options
class LayoutDirection:
    FILL_ROW = 0
    FILL_COLUMN = 1
    FILL_ROW_FIXED = 2
    FILL_COLUMN_FIXED = 3
    ABSOLUTE_SCROLLABLE = 4
    ABSOLUTE_FIXED = 5
    VERTICAL_ONE_COLUMN = 6
    HORIZONTAL_ONE_ROW = 7
    CIRCULAR = 8


# Window level options
class WindowLevel:
    NORMAL = 0
    FLOATING = 3
    DOCK = 20
    MAIN_MENU = 24
    CUSTOM = -1


# When to show the menu
class Visibility:
    ON_LAUNCH = 0
    VIA_ACTION = 1


# Background/icon type options
class BackgroundType:
    NONE = 0
    DATA = 1
    SF_SYMBOL = 2
    FILE = 3
    COLOR = 4
    LINEAR_GRADIENT = 5
    RADIAL_GRADIENT = 6
    PRESET_FILE = 7
    INTERNAL = 8


# Icon position options
class IconPosition:
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    CENTER = 4
    NONE = 5


# =============================================================================
# Input Models for Floating Menu Tools
# =============================================================================


class GetFloatingMenusInput(BaseModel):
    """Input for retrieving floating menus from BTT."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    app_bundle_identifier: Optional[str] = Field(
        default=None,
        description="Get floating menus for a specific app (e.g., 'com.apple.Safari')",
    )
    response_format: ResponseFormat = Field(
        default="markdown",
        description="Output format: 'markdown' or 'json'",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class GetFloatingMenuInput(BaseModel):
    """Input for getting a single floating menu by UUID."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the floating menu to retrieve",
        min_length=36,
        max_length=36,
    )
    response_format: ResponseFormat = Field(
        default="markdown",
        description="Output format: 'markdown' or 'json'",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class CreateFloatingMenuInput(BaseModel):
    """Input for creating a new floating menu.

    Creates a floating menu with sensible defaults. For advanced configuration,
    use btt_add_trigger with full JSON.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(
        ...,
        description="Display name for the floating menu",
        min_length=1,
    )
    # Positioning
    positioning_type: int = Field(
        default=PositioningType.FIXED_POSITION,
        description="0=freeMove, 1=fixedPosition (default), 2=menubarStatusItem",
    )
    position_relative_to: int = Field(
        default=PositionRelativeTo.SCREEN_WITH_MOUSE,
        description="Position relative to: 0=focusedWindow, 1=screenWithMouse, 7=mouse",
    )
    anchor_menu: int = Field(
        default=AnchorPosition.CENTER,
        description="0=topLeft, 1=topRight, 2=botLeft, 3=botRight, 4=center",
    )
    anchor_relation: int = Field(
        default=AnchorPosition.CENTER,
        description="0=topLeft, 1=topRight, 2=botLeft, 3=botRight, 4=center",
    )
    offset_x: int = Field(
        default=0,
        description="Horizontal offset from anchor position",
    )
    offset_y: int = Field(
        default=0,
        description="Vertical offset from anchor position",
    )
    # Size
    width: int = Field(
        default=300,
        description="Menu width in pixels",
        ge=50,
    )
    height: int = Field(
        default=200,
        description="Menu height in pixels",
        ge=50,
    )
    # Layout
    layout_direction: int = Field(
        default=LayoutDirection.FILL_COLUMN,
        description="0=fillRow, 1=fillColumn, 6=vertical, 7=horizontal, 8=circular",
    )
    vertical_spacing: int = Field(
        default=5,
        description="Vertical spacing between items in pixels",
    )
    horizontal_spacing: int = Field(
        default=5,
        description="Horizontal spacing between items in pixels",
    )
    # Appearance
    window_level: int = Field(
        default=WindowLevel.FLOATING,
        description="Window level: 0=normal, 3=floating, 20=dock, 24=mainMenu",
    )
    opacity: float = Field(
        default=1.0,
        description="Menu opacity (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    corner_radius: int = Field(
        default=10,
        description="Corner radius for the menu",
        ge=0,
    )
    background_color: Optional[str] = Field(
        default=None,
        description="Background color in 'R,G,B,A' format (e.g., '40,40,40,230')",
    )
    # Visibility
    visibility: int = Field(
        default=Visibility.VIA_ACTION,
        description="0=showOnLaunch, 1=showViaAction (default)",
    )
    close_on_outside_click: bool = Field(
        default=True,
        description="Close the menu when clicking outside",
    )
    close_after_action: bool = Field(
        default=True,
        description="Close the menu after an action is triggered",
    )
    # App-specific
    app_bundle_identifier: Optional[str] = Field(
        default=None,
        description="Make menu app-specific (e.g., 'com.apple.Safari')",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class AddFloatingMenuItemInput(BaseModel):
    """Input for adding an item to a floating menu."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    menu_uuid: str = Field(
        ...,
        description="UUID of the floating menu to add the item to",
        min_length=36,
        max_length=36,
    )
    name: str = Field(
        ...,
        description="Display name/text for the menu item",
    )
    item_type: int = Field(
        default=FloatingMenuTriggerType.STANDARD_ITEM,
        description="773=button, 774=submenu, 775=slider, 776=textField, 778=webView",
    )
    # Size
    min_width: Optional[int] = Field(
        default=None,
        description="Minimum width of the item",
    )
    min_height: Optional[int] = Field(
        default=None,
        description="Minimum height of the item",
    )
    # Appearance
    background_color: Optional[str] = Field(
        default=None,
        description="Background color in 'R,G,B,A' format (e.g., '80,80,80,255')",
    )
    background_color_hover: Optional[str] = Field(
        default=None,
        description="Hover background color in 'R,G,B,A' format",
    )
    corner_radius: int = Field(
        default=8,
        description="Corner radius for the item",
        ge=0,
    )
    # Icon/SF Symbol
    sf_symbol_name: Optional[str] = Field(
        default=None,
        description="SF Symbol name (e.g., 'hand.tap', 'gear', 'star.fill')",
    )
    icon_color: Optional[str] = Field(
        default=None,
        description="Icon/SF Symbol color in 'R,G,B,A' format",
    )
    icon_position: int = Field(
        default=IconPosition.LEFT,
        description="Icon position: 0=left, 1=top, 2=right, 3=bottom, 4=center",
    )
    # Actions (JSON array)
    actions_json: Optional[str] = Field(
        default=None,
        description="JSON array of actions to execute when item is clicked",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class UpdateFloatingMenuInput(BaseModel):
    """Input for updating a floating menu's configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the floating menu or item to update",
        min_length=36,
        max_length=36,
    )
    update_json: str = Field(
        ...,
        description="JSON with properties to update (use BTTMenu*/BTTMenuItem* keys)",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class ShowFloatingMenuInput(BaseModel):
    """Input for showing a floating menu."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the floating menu to show",
        min_length=36,
        max_length=36,
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class HideFloatingMenuInput(BaseModel):
    """Input for hiding a floating menu."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the floating menu to hide",
        min_length=36,
        max_length=36,
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class ToggleFloatingMenuInput(BaseModel):
    """Input for toggling a floating menu's visibility."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the floating menu to toggle",
        min_length=36,
        max_length=36,
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )
