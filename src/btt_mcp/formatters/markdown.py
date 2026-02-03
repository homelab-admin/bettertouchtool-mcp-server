"""
Markdown formatters for BTT data structures.
"""

from typing import Any


def format_trigger(trigger: dict[str, Any], indent: int = 0) -> str:
    """Format a single trigger for markdown display.

    Args:
        trigger: Trigger data dictionary from BTT
        indent: Indentation level for nested display

    Returns:
        Markdown-formatted string representing the trigger
    """
    prefix = "  " * indent
    lines = []

    # Get key properties
    name = (
        trigger.get("BTTTriggerName")
        or trigger.get("BTTTouchBarButtonName")
        or "Unnamed"
    )
    uuid = trigger.get("BTTUUID", "N/A")
    enabled = trigger.get("BTTEnabled", 1)
    trigger_class = trigger.get("BTTTriggerClass", "Unknown")

    # Get action info
    action_name = trigger.get("BTTPredefinedActionName", "")

    status = "✅" if enabled else "❌"

    lines.append(f"{prefix}- **{name}** {status}")
    lines.append(f"{prefix}  - UUID: `{uuid}`")
    lines.append(f"{prefix}  - Type: {trigger_class}")

    if action_name:
        lines.append(f"{prefix}  - Action: {action_name}")

    # Check for keyboard shortcut info
    shortcut_key = trigger.get("BTTShortcutKeyCode")
    if shortcut_key is not None:
        modifiers = trigger.get("BTTShortcutModifierKeys", 0)
        lines.append(f"{prefix}  - Key Code: {shortcut_key}, Modifiers: {modifiers}")

    # Check for assigned actions
    assigned_actions = trigger.get("BTTAssignedActions", [])
    if assigned_actions:
        lines.append(f"{prefix}  - Assigned Actions: {len(assigned_actions)}")

    return "\n".join(lines)


def format_triggers_list(
    triggers: list[dict[str, Any]],
    title: str = "Triggers",
) -> str:
    """Format a list of triggers for markdown display.

    Args:
        triggers: List of trigger data dictionaries
        title: Section title for the output

    Returns:
        Markdown-formatted string with all triggers
    """
    if not triggers:
        return f"## {title}\n\nNo triggers found."

    lines = [f"## {title}", f"\nFound {len(triggers)} trigger(s):\n"]

    for trigger in triggers:
        lines.append(format_trigger(trigger))
        lines.append("")  # Blank line between triggers

    return "\n".join(lines)


def format_preset_details(preset_data: list[dict[str, Any]]) -> str:
    """Format preset details for markdown display.

    Args:
        preset_data: List of preset data dictionaries

    Returns:
        Markdown-formatted string with preset details
    """
    if not preset_data:
        return "No preset details found."

    lines = ["## Preset Details\n"]

    for preset in preset_data:
        name = preset.get("name", "Unknown")
        uuid = preset.get("uuid", "N/A")
        activated = preset.get("activated", 0)
        hidden = preset.get("hidden", 0)

        status_map = {0: "Disabled", 1: "Enabled", 2: "Enabled (Master Preset)"}
        status = status_map.get(activated, "Unknown")

        lines.append(f"### {name}")
        lines.append(f"- UUID: `{uuid}`")
        lines.append(f"- Status: {status}")
        lines.append(f"- Hidden: {'Yes' if hidden else 'No'}")
        lines.append("")

    return "\n".join(lines)


def format_floating_menu_item(item: dict[str, Any], indent: int = 1) -> str:
    """Format a single floating menu item for markdown display.

    Args:
        item: Menu item data dictionary from BTT
        indent: Indentation level

    Returns:
        Markdown-formatted string representing the item
    """
    prefix = "  " * indent
    lines = []

    name = item.get("BTTTriggerName") or item.get("BTTMenuName") or "Unnamed Item"
    uuid = item.get("BTTUUID", "N/A")
    enabled = item.get("BTTEnabled", 1)
    trigger_type = item.get("BTTTriggerType", 773)

    # Map trigger types to readable names
    type_names = {
        773: "Button",
        774: "Submenu",
        775: "Slider",
        776: "Text Field",
        777: "Back Button",
        778: "WebView",
        800: "Trackpad Widget",
        801: "Row Breaker",
        802: "Column Breaker",
        810: "Text Area",
        811: "Menu Reference",
    }
    type_name = type_names.get(trigger_type, f"Type {trigger_type}")

    status = "✅" if enabled else "❌"
    lines.append(f"{prefix}- **{name}** ({type_name}) {status}")
    lines.append(f"{prefix}  - UUID: `{uuid}`")

    # Check config for details
    config = item.get("BTTMenuConfig", {})
    if config.get("BTTMenuItemSFSymbolName"):
        lines.append(f"{prefix}  - Icon: SF Symbol `{config['BTTMenuItemSFSymbolName']}`")

    # Check for actions
    actions = item.get("BTTMenuItemActions", [])
    if actions:
        lines.append(f"{prefix}  - Actions: {len(actions)}")

    # Recursively format nested items (for submenus)
    nested_items = item.get("BTTMenuItems", [])
    if nested_items:
        lines.append(f"{prefix}  - Nested Items: {len(nested_items)}")
        for nested in nested_items:
            lines.append(format_floating_menu_item(nested, indent + 1))

    return "\n".join(lines)


def format_floating_menu(menu: dict[str, Any]) -> str:
    """Format a single floating menu for detailed markdown display.

    Args:
        menu: Floating menu data dictionary from BTT

    Returns:
        Markdown-formatted string with full menu details
    """
    lines = []

    name = menu.get("BTTMenuName") or menu.get("BTTTriggerName") or "Unnamed Menu"
    uuid = menu.get("BTTUUID", "N/A")
    enabled = menu.get("BTTEnabled", 1)

    status = "✅ Enabled" if enabled else "❌ Disabled"
    lines.append(f"## Floating Menu: {name}")
    lines.append(f"\n**Status:** {status}")
    lines.append(f"**UUID:** `{uuid}`")

    # Parse config
    config = menu.get("BTTMenuConfig", {})

    # Positioning
    positioning = config.get("BTTMenuPositioningType", 1)
    pos_names = {0: "Free Move", 1: "Fixed Position", 2: "Menubar Status Item"}
    lines.append(f"**Positioning:** {pos_names.get(positioning, f'Type {positioning}')}")

    # Size
    width = config.get("BTTMenuFrameWidth", "auto")
    height = config.get("BTTMenuFrameHeight", "auto")
    lines.append(f"**Size:** {width} x {height}")

    # Layout
    layout = config.get("BTTMenuLayoutDirection", 0)
    layout_names = {
        0: "Fill Row",
        1: "Fill Column",
        6: "Vertical (One Column)",
        7: "Horizontal (One Row)",
        8: "Circular",
    }
    lines.append(f"**Layout:** {layout_names.get(layout, f'Type {layout}')}")

    # Visibility settings
    visibility = config.get("BTTMenuVisibility", 0)
    vis_names = {0: "Show on Launch", 1: "Show via Action"}
    lines.append(f"**Visibility:** {vis_names.get(visibility, f'Type {visibility}')}")

    # Menu items
    items = menu.get("BTTMenuItems", [])
    lines.append(f"\n### Menu Items ({len(items)})\n")

    if items:
        for item in items:
            lines.append(format_floating_menu_item(item))
            lines.append("")
    else:
        lines.append("_No items configured_")

    return "\n".join(lines)


def format_floating_menus_list(menus: list[dict[str, Any]]) -> str:
    """Format a list of floating menus for markdown display.

    Args:
        menus: List of floating menu data dictionaries

    Returns:
        Markdown-formatted string with all menus
    """
    if not menus:
        return "## Floating Menus\n\nNo floating menus found."

    lines = ["## Floating Menus", f"\nFound {len(menus)} floating menu(s):\n"]

    for menu in menus:
        name = menu.get("BTTMenuName") or menu.get("BTTTriggerName") or "Unnamed Menu"
        uuid = menu.get("BTTUUID", "N/A")
        enabled = menu.get("BTTEnabled", 1)

        status = "✅" if enabled else "❌"
        item_count = len(menu.get("BTTMenuItems", []))

        lines.append(f"- **{name}** {status}")
        lines.append(f"  - UUID: `{uuid}`")
        lines.append(f"  - Items: {item_count}")
        lines.append("")

    return "\n".join(lines)
