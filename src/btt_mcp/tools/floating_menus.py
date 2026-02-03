"""
Floating menu management tools for BetterTouchTool.

These tools provide a higher-level interface for creating and managing
floating menus compared to the raw trigger JSON approach.
"""

import json
import uuid as uuid_lib

from btt_mcp.client import btt_request
from btt_mcp.formatters import format_floating_menu, format_floating_menus_list
from btt_mcp.models import ResponseFormat
from btt_mcp.models.floating_menus import (
    AddFloatingMenuItemInput,
    CreateFloatingMenuInput,
    GetFloatingMenuInput,
    GetFloatingMenusInput,
    HideFloatingMenuInput,
    ShowFloatingMenuInput,
    ToggleFloatingMenuInput,
    UpdateFloatingMenuInput,
)
from btt_mcp.server import mcp

# Floating menu trigger type ID
FLOATING_MENU_TRIGGER_TYPE = 767


@mcp.tool(
    name="btt_get_floating_menus",
    annotations={
        "title": "Get Floating Menus",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_get_floating_menus(params: GetFloatingMenusInput) -> str:
    """Retrieve all floating menus from BetterTouchTool.

    Returns a list of all configured floating menus, optionally filtered
    by app bundle identifier.

    Args:
        params: Filter parameters and response format options.

    Returns:
        List of floating menus in markdown or JSON format.
    """
    request_params = {"trigger_id": FLOATING_MENU_TRIGGER_TYPE}

    if params.app_bundle_identifier:
        request_params["trigger_app_bundle_identifier"] = params.app_bundle_identifier

    result = await btt_request("get_triggers", request_params, params.connection)

    if result.startswith("Error:"):
        return result

    if params.response_format == ResponseFormat.JSON:
        return result

    try:
        menus = json.loads(result)
        if not isinstance(menus, list):
            menus = [menus]
        return format_floating_menus_list(menus)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_get_floating_menu",
    annotations={
        "title": "Get Single Floating Menu",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_get_floating_menu(params: GetFloatingMenuInput) -> str:
    """Retrieve a specific floating menu by UUID.

    Returns the complete configuration of a floating menu including
    all its items and their properties.

    Args:
        params: Contains the UUID of the floating menu to retrieve.

    Returns:
        Floating menu configuration in markdown or JSON format.
    """
    result = await btt_request("get_trigger", {"uuid": params.uuid}, params.connection)

    if result.startswith("Error:"):
        return result

    if params.response_format == ResponseFormat.JSON:
        return result

    try:
        menu = json.loads(result)
        return format_floating_menu(menu)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_create_floating_menu",
    annotations={
        "title": "Create Floating Menu",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def btt_create_floating_menu(params: CreateFloatingMenuInput) -> str:
    """Create a new floating menu with sensible defaults.

    Creates a floating menu that can be shown/hidden via actions.
    Use btt_add_floating_menu_item to add items to it.

    Args:
        params: Menu configuration including name, position, size, and appearance.

    Returns:
        UUID of the created floating menu, or error message.
    """
    menu_uuid = str(uuid_lib.uuid4()).upper()

    # Build the menu configuration
    config = {
        # Positioning
        "BTTMenuPositioningType": params.positioning_type,
        "BTTMenuPositionRelativeTo": params.position_relative_to,
        "BTTMenuAnchorMenu": params.anchor_menu,
        "BTTMenuAnchorRelation": params.anchor_relation,
        "BTTMenuOffsetX": params.offset_x,
        "BTTMenuOffsetY": params.offset_y,
        # Size
        "BTTMenuFrameWidth": params.width,
        "BTTMenuFrameHeight": params.height,
        "BTTMenuSizingBehavior": 1,  # Fixed size
        # Layout
        "BTTMenuLayoutDirection": params.layout_direction,
        "BTTMenuVerticalSpacing": params.vertical_spacing,
        "BTTMenuHorizontalSpacing": params.horizontal_spacing,
        # Appearance
        "BTTMenuWindowLevel": params.window_level,
        "BTTMenuOpacityActive": params.opacity,
        "BTTMenuOpacityInactive": params.opacity * 0.9,
        "BTTMenuItemCornerRadius": params.corner_radius,
        # Visibility
        "BTTMenuVisibility": params.visibility,
        "BTTMenuCloseOnOutsideClick": 1 if params.close_on_outside_click else 0,
        "BTTMenuCloseAfterAction": 1 if params.close_after_action else 0,
    }

    if params.background_color:
        config["BTTMenuItemBackgroundType"] = 4  # Color
        config["BTTMenuItemBackgroundColor"] = params.background_color

    # Build the trigger JSON
    trigger = {
        "BTTTriggerType": FLOATING_MENU_TRIGGER_TYPE,
        "BTTTriggerClass": "BTTTriggerTypeFloatingMenu",
        "BTTUUID": menu_uuid,
        "BTTEnabled": 1,
        "BTTTriggerName": f"Floating Menu: {params.name}",
        "BTTMenuName": params.name,
        "BTTMenuConfig": config,
        "BTTMenuItems": [],  # Empty, items added separately
        "BTTMenuAvailability": 0,  # Everywhere
    }

    if params.app_bundle_identifier:
        trigger["BTTAppBundleIdentifier"] = params.app_bundle_identifier

    trigger_json = json.dumps(trigger)
    result = await btt_request(
        "add_new_trigger", {"json": trigger_json}, params.connection
    )

    if result.startswith("Error:"):
        return result

    # BTT returns the UUID on success
    if result and result.strip():
        return result.strip()

    return menu_uuid


def _build_menu_item_config(params: AddFloatingMenuItemInput) -> dict:
    """Build the BTT config dict for a floating menu item."""
    config: dict = {
        "BTTMenuItemVisibleWhileActive": 1,
        "BTTMenuItemVisibleWhileInactive": 1,
        "BTTMenuItemCornerRadius": params.corner_radius,
    }

    if params.min_width:
        config["BTTMenuItemMinWidth"] = params.min_width
    if params.min_height:
        config["BTTMenuItemMinHeight"] = params.min_height

    if params.background_color:
        config["BTTMenuItemBackgroundType"] = 4  # Color
        config["BTTMenuItemBackgroundColor"] = params.background_color

    if params.background_color_hover:
        config["BTTMenuItemBackgroundColorHover"] = params.background_color_hover

    if params.sf_symbol_name:
        config["BTTMenuItemIconType"] = 2  # SF Symbol
        config["BTTMenuItemSFSymbolName"] = params.sf_symbol_name
        config["BTTMenuItemIconPosition"] = params.icon_position
        if params.icon_color:
            config["BTTMenuItemIconColor1"] = params.icon_color

    return config


@mcp.tool(
    name="btt_add_floating_menu_item",
    annotations={
        "title": "Add Floating Menu Item",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def btt_add_floating_menu_item(params: AddFloatingMenuItemInput) -> str:
    """Add an item (button, slider, text field, etc.) to a floating menu.

    Creates a new item in the specified floating menu. The item can have
    actions assigned to it.

    Args:
        params: Item configuration including name, type, appearance, and actions.

    Returns:
        UUID of the created item, or error message.
    """
    item_uuid = str(uuid_lib.uuid4()).upper()

    # Build the item configuration
    config = _build_menu_item_config(params)

    # Build the item trigger JSON
    item = {
        "BTTTriggerType": params.item_type,
        "BTTTriggerParentUUID": params.menu_uuid,
        "BTTUUID": item_uuid,
        "BTTEnabled": 1,
        "BTTTriggerName": params.name,
        "BTTMenuName": params.name,
        "BTTMenuConfig": config,
    }

    # Add actions if provided
    if params.actions_json:
        try:
            actions = json.loads(params.actions_json)
            item["BTTMenuItemActions"] = actions
        except json.JSONDecodeError:
            return "Error: Invalid actions_json - must be a valid JSON array"

    item_json = json.dumps(item)
    result = await btt_request(
        "add_new_trigger",
        {"json": item_json, "trigger_parent_uuid": params.menu_uuid},
        params.connection,
    )

    if result.startswith("Error:"):
        return result

    if result and result.strip():
        return result.strip()

    return item_uuid


@mcp.tool(
    name="btt_update_floating_menu",
    annotations={
        "title": "Update Floating Menu",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_update_floating_menu(params: UpdateFloatingMenuInput) -> str:
    """Update a floating menu or menu item's configuration.

    Provide the UUID and a JSON object with the properties to update.
    Use BTTMenu* prefixes for menu config, BTTMenuItem* for item config.

    Args:
        params: Contains UUID and JSON with properties to update.

    Returns:
        Confirmation of update.
    """
    result = await btt_request(
        "update_trigger",
        {"uuid": params.uuid, "json": params.update_json},
        params.connection,
    )

    if result.startswith("Error:"):
        return result

    if not result or result.strip() == "":
        return "Floating menu updated successfully."

    return result


@mcp.tool(
    name="btt_show_floating_menu",
    annotations={
        "title": "Show Floating Menu",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_show_floating_menu(params: ShowFloatingMenuInput) -> str:
    """Show a floating menu by UUID.

    Makes the floating menu visible on screen.

    Args:
        params: Contains the UUID of the floating menu to show.

    Returns:
        Confirmation message.
    """
    # Use the trigger_action endpoint with show floating menu action
    action = {
        "BTTPredefinedActionType": 367,  # Show Floating Menu
        "BTTPredefinedActionName": "Show Floating HTML Menu",
        "BTTFloatingMenuUUID": params.uuid,
    }

    result = await btt_request(
        "trigger_action", {"json": json.dumps(action)}, params.connection
    )

    if result.startswith("Error:"):
        return result

    return "Floating menu shown."


@mcp.tool(
    name="btt_hide_floating_menu",
    annotations={
        "title": "Hide Floating Menu",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_hide_floating_menu(params: HideFloatingMenuInput) -> str:
    """Hide a floating menu by UUID.

    Makes the floating menu invisible.

    Args:
        params: Contains the UUID of the floating menu to hide.

    Returns:
        Confirmation message.
    """
    action = {
        "BTTPredefinedActionType": 368,  # Hide Floating Menu
        "BTTPredefinedActionName": "Hide Floating HTML Menu",
        "BTTFloatingMenuUUID": params.uuid,
    }

    result = await btt_request(
        "trigger_action", {"json": json.dumps(action)}, params.connection
    )

    if result.startswith("Error:"):
        return result

    return "Floating menu hidden."


@mcp.tool(
    name="btt_toggle_floating_menu",
    annotations={
        "title": "Toggle Floating Menu",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def btt_toggle_floating_menu(params: ToggleFloatingMenuInput) -> str:
    """Toggle a floating menu's visibility.

    If visible, hides it. If hidden, shows it.

    Args:
        params: Contains the UUID of the floating menu to toggle.

    Returns:
        Confirmation message.
    """
    action = {
        "BTTPredefinedActionType": 369,  # Toggle Floating Menu
        "BTTPredefinedActionName": "Toggle Floating HTML Menu",
        "BTTFloatingMenuUUID": params.uuid,
    }

    result = await btt_request(
        "trigger_action", {"json": json.dumps(action)}, params.connection
    )

    if result.startswith("Error:"):
        return result

    return "Floating menu toggled."
