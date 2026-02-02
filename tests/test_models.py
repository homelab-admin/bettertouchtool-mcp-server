"""
Tests for BTT MCP models.
"""

import pytest
from pydantic import ValidationError

from btt_mcp.models import (
    BTTConnectionConfig,
    ExportPresetInput,
    GetClipboardInput,
    GetTriggerInput,
    GetTriggersInput,
    GetVariableInput,
    ResponseFormat,
    SetVariableInput,
    TriggerNamedInput,
    UpdateWidgetInput,
)


class TestBTTConnectionConfig:
    """Tests for BTTConnectionConfig."""

    def test_default_values(self):
        config = BTTConnectionConfig()
        assert config.host == "127.0.0.1"
        assert config.port == 12345
        assert config.shared_secret is None
        assert config.use_cli is False

    def test_custom_values(self):
        config = BTTConnectionConfig(
            host="192.168.1.1",
            port=8080,
            shared_secret="mysecret",
            use_cli=True,
        )
        assert config.host == "192.168.1.1"
        assert config.port == 8080
        assert config.shared_secret == "mysecret"
        assert config.use_cli is True

    def test_port_validation(self):
        with pytest.raises(ValidationError):
            BTTConnectionConfig(port=0)
        with pytest.raises(ValidationError):
            BTTConnectionConfig(port=70000)


class TestResponseFormat:
    """Tests for ResponseFormat enum."""

    def test_values(self):
        assert ResponseFormat.MARKDOWN == "markdown"
        assert ResponseFormat.JSON == "json"


class TestTriggerModels:
    """Tests for trigger-related models."""

    def test_get_triggers_defaults(self):
        params = GetTriggersInput()
        assert params.trigger_type is None
        assert params.trigger_id is None
        assert params.response_format == ResponseFormat.MARKDOWN

    def test_get_trigger_requires_uuid(self):
        with pytest.raises(ValidationError):
            GetTriggerInput()

    def test_get_trigger_uuid_length(self):
        with pytest.raises(ValidationError):
            GetTriggerInput(uuid="short")

    def test_get_trigger_valid(self):
        uuid = "12345678-1234-1234-1234-123456789012"
        params = GetTriggerInput(uuid=uuid)
        assert params.uuid == uuid


class TestActionModels:
    """Tests for action-related models."""

    def test_trigger_named_requires_name(self):
        with pytest.raises(ValidationError):
            TriggerNamedInput()

    def test_trigger_named_valid(self):
        params = TriggerNamedInput(trigger_name="My Trigger")
        assert params.trigger_name == "My Trigger"
        assert params.wait_for_reply is True


class TestVariableModels:
    """Tests for variable-related models."""

    def test_get_variable_requires_name(self):
        with pytest.raises(ValidationError):
            GetVariableInput()

    def test_set_variable_defaults(self):
        params = SetVariableInput(variable_name="test", value="123")
        assert params.variable_type == "string"
        assert params.persistent is False


class TestWidgetModels:
    """Tests for widget-related models."""

    def test_update_widget_requires_uuid(self):
        with pytest.raises(ValidationError):
            UpdateWidgetInput()

    def test_update_widget_defaults(self):
        uuid = "12345678-1234-1234-1234-123456789012"
        params = UpdateWidgetInput(uuid=uuid)
        assert params.widget_type == "touch_bar"
        assert params.text is None


class TestClipboardModels:
    """Tests for clipboard-related models."""

    def test_get_clipboard_defaults(self):
        params = GetClipboardInput()
        assert params.format == "NSPasteboardTypeString"
        assert params.as_base64 is False


class TestPresetModels:
    """Tests for preset-related models."""

    def test_export_preset_requires_fields(self):
        with pytest.raises(ValidationError):
            ExportPresetInput()

    def test_export_preset_valid(self):
        params = ExportPresetInput(name="My Preset", output_path="/tmp/preset.btt")
        assert params.compress is True
        assert params.include_settings is False
