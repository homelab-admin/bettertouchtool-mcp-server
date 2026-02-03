"""
Pydantic input models for BTT MCP tools.
"""

from btt_mcp.models.actions import TriggerActionInput, TriggerNamedInput
from btt_mcp.models.clipboard import GetClipboardInput, SetClipboardInput
from btt_mcp.models.common import BTTConnectionConfig, ResponseFormat
from btt_mcp.models.floating_menus import (
    AddFloatingMenuItemInput,
    CreateFloatingMenuInput,
    FloatingMenuTriggerType,
    GetFloatingMenuInput,
    GetFloatingMenusInput,
    HideFloatingMenuInput,
    ShowFloatingMenuInput,
    ToggleFloatingMenuInput,
    UpdateFloatingMenuInput,
)
from btt_mcp.models.presets import (
    DisplayNotificationInput,
    ExportPresetInput,
    GetPresetDetailsInput,
    ImportPresetInput,
    RevealElementInput,
)
from btt_mcp.models.triggers import (
    AddTriggerInput,
    DeleteTriggerInput,
    ExecuteTriggerInput,
    GetTriggerInput,
    GetTriggersInput,
    ListNamedTriggersInput,
    UpdateTriggerInput,
)
from btt_mcp.models.variables import GetVariableInput, SetVariableInput
from btt_mcp.models.widgets import RefreshWidgetInput, UpdateWidgetInput

__all__ = [
    # Common
    "ResponseFormat",
    "BTTConnectionConfig",
    # Triggers
    "GetTriggersInput",
    "GetTriggerInput",
    "AddTriggerInput",
    "UpdateTriggerInput",
    "DeleteTriggerInput",
    "ExecuteTriggerInput",
    "ListNamedTriggersInput",
    # Actions
    "TriggerNamedInput",
    "TriggerActionInput",
    # Variables
    "GetVariableInput",
    "SetVariableInput",
    # Widgets
    "UpdateWidgetInput",
    "RefreshWidgetInput",
    # Clipboard
    "GetClipboardInput",
    "SetClipboardInput",
    # Presets
    "ExportPresetInput",
    "ImportPresetInput",
    "GetPresetDetailsInput",
    "DisplayNotificationInput",
    "RevealElementInput",
    # Floating Menus
    "FloatingMenuTriggerType",
    "GetFloatingMenusInput",
    "GetFloatingMenuInput",
    "CreateFloatingMenuInput",
    "AddFloatingMenuItemInput",
    "UpdateFloatingMenuInput",
    "ShowFloatingMenuInput",
    "HideFloatingMenuInput",
    "ToggleFloatingMenuInput",
]
