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
