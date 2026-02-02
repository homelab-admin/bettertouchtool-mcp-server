"""
Tests for BTT MCP formatters.
"""

from btt_mcp.formatters import (
    format_preset_details,
    format_trigger,
    format_triggers_list,
)


class TestFormatTrigger:
    """Tests for trigger formatting."""

    def test_basic_trigger(self):
        trigger = {
            "BTTTriggerName": "Test Trigger",
            "BTTUUID": "12345678-1234-1234-1234-123456789012",
            "BTTEnabled": 1,
            "BTTTriggerClass": "BTTTriggerTypeKeyboardShortcut",
        }
        result = format_trigger(trigger)
        assert "**Test Trigger**" in result
        assert "✅" in result
        assert "12345678-1234-1234-1234-123456789012" in result

    def test_disabled_trigger(self):
        trigger = {
            "BTTTriggerName": "Disabled",
            "BTTUUID": "test-uuid-1234-1234-123456789012",
            "BTTEnabled": 0,
        }
        result = format_trigger(trigger)
        assert "❌" in result

    def test_unnamed_trigger(self):
        trigger = {"BTTUUID": "test-uuid-1234-1234-123456789012"}
        result = format_trigger(trigger)
        assert "**Unnamed**" in result

    def test_touch_bar_name_fallback(self):
        trigger = {
            "BTTTouchBarButtonName": "Touch Bar Button",
            "BTTUUID": "test-uuid-1234-1234-123456789012",
        }
        result = format_trigger(trigger)
        assert "**Touch Bar Button**" in result

    def test_with_keyboard_shortcut(self):
        trigger = {
            "BTTTriggerName": "Shortcut",
            "BTTUUID": "test-uuid-1234-1234-123456789012",
            "BTTShortcutKeyCode": 0,
            "BTTShortcutModifierKeys": 256,
        }
        result = format_trigger(trigger)
        assert "Key Code: 0" in result
        assert "Modifiers: 256" in result

    def test_with_assigned_actions(self):
        trigger = {
            "BTTTriggerName": "With Actions",
            "BTTUUID": "test-uuid-1234-1234-123456789012",
            "BTTAssignedActions": [{}, {}, {}],
        }
        result = format_trigger(trigger)
        assert "Assigned Actions: 3" in result

    def test_indentation(self):
        trigger = {
            "BTTTriggerName": "Indented",
            "BTTUUID": "test-uuid-1234-1234-123456789012",
        }
        result = format_trigger(trigger, indent=2)
        assert result.startswith("    -")  # 2 levels of indentation


class TestFormatTriggersList:
    """Tests for trigger list formatting."""

    def test_empty_list(self):
        result = format_triggers_list([])
        assert "No triggers found" in result

    def test_single_trigger(self):
        triggers = [
            {
                "BTTTriggerName": "Test",
                "BTTUUID": "test-uuid-1234-1234-123456789012",
            }
        ]
        result = format_triggers_list(triggers)
        assert "Found 1 trigger(s)" in result
        assert "**Test**" in result

    def test_multiple_triggers(self):
        triggers = [
            {"BTTTriggerName": "First", "BTTUUID": "uuid-1"},
            {"BTTTriggerName": "Second", "BTTUUID": "uuid-2"},
        ]
        result = format_triggers_list(triggers)
        assert "Found 2 trigger(s)" in result

    def test_custom_title(self):
        result = format_triggers_list([], title="Named Triggers")
        assert "## Named Triggers" in result


class TestFormatPresetDetails:
    """Tests for preset details formatting."""

    def test_empty_list(self):
        result = format_preset_details([])
        assert "No preset details found" in result

    def test_single_preset(self):
        presets = [
            {
                "name": "My Preset",
                "uuid": "preset-uuid-1234",
                "activated": 1,
                "hidden": 0,
            }
        ]
        result = format_preset_details(presets)
        assert "### My Preset" in result
        assert "Enabled" in result
        assert "Hidden: No" in result

    def test_master_preset(self):
        presets = [{"name": "Master", "activated": 2}]
        result = format_preset_details(presets)
        assert "Enabled (Master Preset)" in result

    def test_hidden_preset(self):
        presets = [{"name": "Hidden", "hidden": 1}]
        result = format_preset_details(presets)
        assert "Hidden: Yes" in result
