#!/usr/bin/env python3
"""
BetterTouchTool MCP Server

An MCP server for understanding, explaining, and managing BetterTouchTool configurations.
Supports HTTP webserver, CLI (bttcli), and Unix socket communication methods.

Author: Created for Christian's BTT management needs
"""

import json
import subprocess
import urllib.parse
import os
from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# Initialize the MCP server
mcp = FastMCP("btt_mcp")

# =============================================================================
# Configuration Constants
# =============================================================================

DEFAULT_BTT_PORT = 12345
DEFAULT_BTT_HOST = "127.0.0.1"
BTT_SOCKET_PATH = "/tmp/com.hegenberg.BetterTouchTool.sock"
BTTCLI_PATH = "/Applications/BetterTouchTool.app/Contents/SharedSupport/bin/bttcli"

# Common trigger types for reference
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

# Named triggers have trigger_id = 643
NAMED_TRIGGER_ID = 643


# =============================================================================
# Pydantic Input Models
# =============================================================================

class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class BTTConnectionConfig(BaseModel):
    """Configuration for connecting to BetterTouchTool."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    host: str = Field(
        default=DEFAULT_BTT_HOST,
        description="BTT webserver host (default: 127.0.0.1)"
    )
    port: int = Field(
        default=DEFAULT_BTT_PORT,
        description="BTT webserver port (default: 12345)",
        ge=1,
        le=65535
    )
    shared_secret: Optional[str] = Field(
        default=None,
        description="Shared secret for BTT webserver authentication (if configured)"
    )
    use_cli: bool = Field(
        default=False,
        description="Use bttcli instead of HTTP (faster, uses Unix socket)"
    )


class GetTriggersInput(BaseModel):
    """Input for retrieving triggers from BTT."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    trigger_type: Optional[str] = Field(
        default=None,
        description="Filter by trigger type (e.g., 'BTTTriggerTypeKeyboardShortcut', 'BTTTriggerTypeTouchBar')"
    )
    trigger_id: Optional[int] = Field(
        default=None,
        description="Filter by trigger ID (e.g., 643 for named triggers)"
    )
    trigger_parent_uuid: Optional[str] = Field(
        default=None,
        description="Get triggers within a specific parent group/folder by UUID"
    )
    trigger_uuid: Optional[str] = Field(
        default=None,
        description="Get a specific trigger by UUID"
    )
    app_bundle_identifier: Optional[str] = Field(
        default=None,
        description="Get triggers for a specific app (e.g., 'com.apple.Safari')"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for raw data"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class GetTriggerInput(BaseModel):
    """Input for getting a single trigger by UUID."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    uuid: str = Field(
        ...,
        description="UUID of the trigger to retrieve",
        min_length=36,
        max_length=36
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for raw data"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class TriggerNamedInput(BaseModel):
    """Input for triggering a named trigger."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    trigger_name: str = Field(
        ...,
        description="Name of the named trigger to execute",
        min_length=1
    )
    wait_for_reply: bool = Field(
        default=True,
        description="Wait for the trigger to complete and return result"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class TriggerActionInput(BaseModel):
    """Input for triggering a BTT action via JSON definition."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    action_json: str = Field(
        ...,
        description="JSON definition of the action to trigger (copy from BTT via right-click -> Copy JSON)"
    )
    wait_for_reply: bool = Field(
        default=False,
        description="Wait for the action to complete"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class ExecuteTriggerInput(BaseModel):
    """Input for executing all actions assigned to a trigger."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    uuid: str = Field(
        ...,
        description="UUID of the trigger whose actions should be executed",
        min_length=36,
        max_length=36
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class AddTriggerInput(BaseModel):
    """Input for adding a new trigger to BTT."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    trigger_json: str = Field(
        ...,
        description="JSON definition of the new trigger (copy format from existing trigger)"
    )
    parent_uuid: Optional[str] = Field(
        default=None,
        description="UUID of parent group/folder to add trigger to"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class UpdateTriggerInput(BaseModel):
    """Input for updating an existing trigger."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    uuid: str = Field(
        ...,
        description="UUID of the trigger to update",
        min_length=36,
        max_length=36
    )
    update_json: str = Field(
        ...,
        description="JSON with the properties to update"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class DeleteTriggerInput(BaseModel):
    """Input for deleting a trigger."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    uuid: str = Field(
        ...,
        description="UUID of the trigger to delete",
        min_length=36,
        max_length=36
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class GetVariableInput(BaseModel):
    """Input for getting a BTT variable."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    variable_name: str = Field(
        ...,
        description="Name of the variable to retrieve",
        min_length=1
    )
    variable_type: str = Field(
        default="string",
        description="Type of variable: 'string' or 'number'"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class SetVariableInput(BaseModel):
    """Input for setting a BTT variable."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    variable_name: str = Field(
        ...,
        description="Name of the variable to set",
        min_length=1
    )
    value: str = Field(
        ...,
        description="Value to set (will be converted to number if variable_type is 'number')"
    )
    variable_type: str = Field(
        default="string",
        description="Type of variable: 'string' or 'number'"
    )
    persistent: bool = Field(
        default=False,
        description="If True, variable persists across BTT restarts"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class UpdateWidgetInput(BaseModel):
    """Input for updating a widget (Touch Bar, Menubar, Stream Deck)."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    uuid: str = Field(
        ...,
        description="UUID of the widget to update",
        min_length=36,
        max_length=36
    )
    widget_type: str = Field(
        default="touch_bar",
        description="Type of widget: 'touch_bar', 'menubar', or 'stream_deck'"
    )
    text: Optional[str] = Field(
        default=None,
        description="New text to display on the widget"
    )
    icon_path: Optional[str] = Field(
        default=None,
        description="Path to icon file to display"
    )
    icon_data: Optional[str] = Field(
        default=None,
        description="Base64-encoded icon data"
    )
    background_color: Optional[str] = Field(
        default=None,
        description="Background color as 'R,G,B,A' (e.g., '200,100,100,255')"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class RefreshWidgetInput(BaseModel):
    """Input for refreshing a script widget."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    uuid: str = Field(
        ...,
        description="UUID of the widget to refresh",
        min_length=36,
        max_length=36
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class GetClipboardInput(BaseModel):
    """Input for getting clipboard content."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    format: str = Field(
        default="NSPasteboardTypeString",
        description="Clipboard format (e.g., 'NSPasteboardTypeString', 'NSPasteboardTypeHTML', 'all')"
    )
    as_base64: bool = Field(
        default=False,
        description="Return content as base64 encoded"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class SetClipboardInput(BaseModel):
    """Input for setting clipboard content."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    content: str = Field(
        ...,
        description="Content to put in clipboard"
    )
    format: str = Field(
        default="NSPasteboardTypeString",
        description="Clipboard format (e.g., 'NSPasteboardTypeString', 'NSPasteboardTypeHTML')"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class ExportPresetInput(BaseModel):
    """Input for exporting a preset."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    name: str = Field(
        ...,
        description="Name of the preset to export",
        min_length=1
    )
    output_path: str = Field(
        ...,
        description="Path where the preset file should be saved"
    )
    compress: bool = Field(
        default=True,
        description="Compress the exported preset"
    )
    include_settings: bool = Field(
        default=False,
        description="Include BTT settings in export"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class ImportPresetInput(BaseModel):
    """Input for importing a preset."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    path: str = Field(
        ...,
        description="Path to the preset file to import"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class GetPresetDetailsInput(BaseModel):
    """Input for getting preset details."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    name: str = Field(
        ...,
        description="Name of the preset to query",
        min_length=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for raw data"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class DisplayNotificationInput(BaseModel):
    """Input for displaying a notification."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    title: str = Field(
        ...,
        description="Notification title",
        min_length=1
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="Notification subtitle"
    )
    sound_name: Optional[str] = Field(
        default=None,
        description="Name of sound to play (e.g., 'frog', 'Ping')"
    )
    image_path: Optional[str] = Field(
        default=None,
        description="Path to image to display in notification"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class RevealElementInput(BaseModel):
    """Input for revealing an element in BTT UI."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    uuid: str = Field(
        ...,
        description="UUID of the element to reveal in BTT UI",
        min_length=36,
        max_length=36
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


class ListNamedTriggersInput(BaseModel):
    """Input for listing all named triggers."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for raw data"
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration"
    )


# =============================================================================
# HTTP Client Utilities
# =============================================================================

def _build_url(endpoint: str, params: Dict[str, Any], config: BTTConnectionConfig) -> str:
    """Build the BTT webserver URL with parameters."""
    base_url = f"http://{config.host}:{config.port}/{endpoint}/"
    
    # Add shared secret if configured
    if config.shared_secret:
        params['shared_secret'] = config.shared_secret
    
    # Filter out None values and encode parameters
    filtered_params = {k: v for k, v in params.items() if v is not None}
    
    if filtered_params:
        query_string = urllib.parse.urlencode(filtered_params, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"
    
    return base_url


async def _http_request(endpoint: str, params: Dict[str, Any], config: BTTConnectionConfig) -> str:
    """Make an HTTP request to the BTT webserver."""
    url = _build_url(endpoint, params, config)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                return "Error: Authentication failed. Check your shared_secret configuration."
            return f"Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.ConnectError:
            return f"Error: Could not connect to BTT webserver at {config.host}:{config.port}. Is the webserver enabled in BTT preferences?"
        except httpx.TimeoutException:
            return "Error: Request timed out. BTT may be busy or unresponsive."


def _cli_request(method: str, params: Dict[str, Any]) -> str:
    """Make a request using bttcli."""
    # Check if bttcli exists
    cli_path = BTTCLI_PATH
    if not os.path.exists(cli_path):
        # Try alternate location
        cli_path = os.path.expanduser("~/Applications/BetterTouchTool.app/Contents/SharedSupport/bin/bttcli")
        if not os.path.exists(cli_path):
            return "Error: bttcli not found. Make sure BetterTouchTool is installed."
    
    # Build command
    cmd = [cli_path, method]
    for key, value in params.items():
        if value is not None:
            cmd.append(f"{key}={value}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return f"Error: bttcli failed - {result.stderr}"
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Error: bttcli timed out"
    except FileNotFoundError:
        return f"Error: bttcli not found at {cli_path}"


async def _btt_request(endpoint: str, params: Dict[str, Any], config: BTTConnectionConfig) -> str:
    """Make a request to BTT using configured method (HTTP or CLI)."""
    if config.use_cli:
        return _cli_request(endpoint, params)
    return await _http_request(endpoint, params, config)


# =============================================================================
# Formatting Utilities
# =============================================================================

def _format_trigger(trigger: Dict[str, Any], indent: int = 0) -> str:
    """Format a single trigger for markdown display."""
    prefix = "  " * indent
    lines = []
    
    # Get key properties
    name = trigger.get('BTTTriggerName') or trigger.get('BTTTouchBarButtonName') or 'Unnamed'
    uuid = trigger.get('BTTUUID', 'N/A')
    enabled = trigger.get('BTTEnabled', 1)
    trigger_class = trigger.get('BTTTriggerClass', 'Unknown')
    
    # Get action info
    action_name = trigger.get('BTTPredefinedActionName', '')
    action_type = trigger.get('BTTPredefinedActionType', '')
    
    status = "✅" if enabled else "❌"
    
    lines.append(f"{prefix}- **{name}** {status}")
    lines.append(f"{prefix}  - UUID: `{uuid}`")
    lines.append(f"{prefix}  - Type: {trigger_class}")
    
    if action_name:
        lines.append(f"{prefix}  - Action: {action_name}")
    
    # Check for keyboard shortcut info
    shortcut_key = trigger.get('BTTShortcutKeyCode')
    if shortcut_key is not None:
        modifiers = trigger.get('BTTShortcutModifierKeys', 0)
        lines.append(f"{prefix}  - Key Code: {shortcut_key}, Modifiers: {modifiers}")
    
    # Check for assigned actions
    assigned_actions = trigger.get('BTTAssignedActions', [])
    if assigned_actions:
        lines.append(f"{prefix}  - Assigned Actions: {len(assigned_actions)}")
    
    return "\n".join(lines)


def _format_triggers_list(triggers: List[Dict[str, Any]], title: str = "Triggers") -> str:
    """Format a list of triggers for markdown display."""
    if not triggers:
        return f"## {title}\n\nNo triggers found."
    
    lines = [f"## {title}", f"\nFound {len(triggers)} trigger(s):\n"]
    
    for trigger in triggers:
        lines.append(_format_trigger(trigger))
        lines.append("")  # Blank line between triggers
    
    return "\n".join(lines)


def _format_preset_details(preset_data: List[Dict[str, Any]]) -> str:
    """Format preset details for markdown display."""
    if not preset_data:
        return "No preset details found."
    
    lines = ["## Preset Details\n"]
    
    for preset in preset_data:
        name = preset.get('name', 'Unknown')
        uuid = preset.get('uuid', 'N/A')
        activated = preset.get('activated', 0)
        hidden = preset.get('hidden', 0)
        
        status_map = {0: "Disabled", 1: "Enabled", 2: "Enabled (Master Preset)"}
        status = status_map.get(activated, "Unknown")
        
        lines.append(f"### {name}")
        lines.append(f"- UUID: `{uuid}`")
        lines.append(f"- Status: {status}")
        lines.append(f"- Hidden: {'Yes' if hidden else 'No'}")
        lines.append("")
    
    return "\n".join(lines)


# =============================================================================
# MCP Tool Implementations
# =============================================================================

@mcp.tool(
    name="btt_get_triggers",
    annotations={
        "title": "Get BTT Triggers",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_get_triggers(params: GetTriggersInput) -> str:
    """Retrieve triggers from BetterTouchTool with optional filtering.
    
    Use this tool to explore and understand the current BTT configuration.
    You can filter by trigger type, parent folder, specific app, or get all triggers.
    
    Args:
        params: Filter parameters including trigger_type, trigger_id, app_bundle_identifier, etc.
    
    Returns:
        List of triggers in markdown or JSON format based on response_format setting.
    """
    request_params = {}
    
    if params.trigger_type:
        request_params['trigger_type'] = params.trigger_type
    if params.trigger_id is not None:
        request_params['trigger_id'] = params.trigger_id
    if params.trigger_parent_uuid:
        request_params['trigger_parent_uuid'] = params.trigger_parent_uuid
    if params.trigger_uuid:
        request_params['trigger_uuid'] = params.trigger_uuid
    if params.app_bundle_identifier:
        request_params['trigger_app_bundle_identifier'] = params.app_bundle_identifier
    
    result = await _btt_request('get_triggers', request_params, params.connection)
    
    # Check for errors
    if result.startswith("Error:"):
        return result
    
    if params.response_format == ResponseFormat.JSON:
        return result
    
    # Parse and format for markdown
    try:
        triggers = json.loads(result)
        if not isinstance(triggers, list):
            triggers = [triggers]
        return _format_triggers_list(triggers)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_get_trigger",
    annotations={
        "title": "Get Single BTT Trigger",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_get_trigger(params: GetTriggerInput) -> str:
    """Retrieve a specific trigger by its UUID.
    
    Use this to get detailed information about a single trigger, including
    all its configuration and assigned actions.
    
    Args:
        params: Contains the UUID of the trigger to retrieve.
    
    Returns:
        Trigger configuration in markdown or JSON format.
    """
    result = await _btt_request('get_trigger', {'uuid': params.uuid}, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    if params.response_format == ResponseFormat.JSON:
        return result
    
    try:
        trigger = json.loads(result)
        return _format_trigger(trigger)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_list_named_triggers",
    annotations={
        "title": "List Named Triggers",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_list_named_triggers(params: ListNamedTriggersInput) -> str:
    """List all named triggers configured in BetterTouchTool.
    
    Named triggers are triggers configured in the 'Other' tab that can be
    called by name from scripts or other actions.
    
    Returns:
        List of named triggers with their names and UUIDs.
    """
    result = await _btt_request('get_triggers', {'trigger_id': NAMED_TRIGGER_ID}, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    if params.response_format == ResponseFormat.JSON:
        return result
    
    try:
        triggers = json.loads(result)
        if not isinstance(triggers, list):
            triggers = [triggers]
        return _format_triggers_list(triggers, "Named Triggers")
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_trigger_named",
    annotations={
        "title": "Trigger Named Action",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def btt_trigger_named(params: TriggerNamedInput) -> str:
    """Execute a named trigger by its name.
    
    Named triggers are configured in BTT's 'Other' tab and can perform
    any sequence of actions.
    
    Args:
        params: Contains the trigger_name and whether to wait for completion.
    
    Returns:
        Result of the trigger execution (if wait_for_reply is True).
    """
    request_params = {
        'trigger_name': params.trigger_name,
        'wait_for_reply': 'true' if params.wait_for_reply else 'false'
    }
    
    result = await _btt_request('trigger_named', request_params, params.connection)
    
    if not result or result.strip() == "":
        return f"Triggered '{params.trigger_name}' successfully."
    
    return result


@mcp.tool(
    name="btt_trigger_action",
    annotations={
        "title": "Trigger BTT Action",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def btt_trigger_action(params: TriggerActionInput) -> str:
    """Trigger any BTT predefined action using a JSON definition.
    
    You can get the JSON for an action by right-clicking a configured
    trigger in BTT and selecting 'Copy JSON'.
    
    Args:
        params: Contains the action JSON definition.
    
    Returns:
        Result of the action execution.
    """
    result = await _btt_request('trigger_action', {'json': params.action_json}, params.connection)
    
    if not result or result.strip() == "":
        return "Action triggered successfully."
    
    return result


@mcp.tool(
    name="btt_execute_trigger",
    annotations={
        "title": "Execute Trigger Actions",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def btt_execute_trigger(params: ExecuteTriggerInput) -> str:
    """Execute all actions assigned to a specific trigger by UUID.
    
    Args:
        params: Contains the UUID of the trigger to execute.
    
    Returns:
        Result of the execution.
    """
    result = await _btt_request('execute_assigned_actions_for_trigger', {'uuid': params.uuid}, params.connection)
    
    if not result or result.strip() == "":
        return f"Executed actions for trigger {params.uuid} successfully."
    
    return result


@mcp.tool(
    name="btt_add_trigger",
    annotations={
        "title": "Add New Trigger",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def btt_add_trigger(params: AddTriggerInput) -> str:
    """Add a new trigger to BetterTouchTool.
    
    The trigger definition should be in JSON format. You can get
    the format by copying an existing trigger's JSON in BTT.
    
    Args:
        params: Contains the trigger JSON definition and optional parent UUID.
    
    Returns:
        Confirmation of trigger creation.
    """
    request_params = {'json': params.trigger_json}
    if params.parent_uuid:
        request_params['trigger_parent_uuid'] = params.parent_uuid
    
    result = await _btt_request('add_new_trigger', request_params, params.connection)
    
    if not result or result.strip() == "":
        return "Trigger added successfully."
    
    return result


@mcp.tool(
    name="btt_update_trigger",
    annotations={
        "title": "Update Trigger",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_update_trigger(params: UpdateTriggerInput) -> str:
    """Update an existing trigger's configuration.
    
    Provide the UUID of the trigger and a JSON object with the
    properties to update.
    
    Args:
        params: Contains UUID and JSON with properties to update.
    
    Returns:
        Confirmation of update.
    """
    request_params = {
        'uuid': params.uuid,
        'json': params.update_json
    }
    
    result = await _btt_request('update_trigger', request_params, params.connection)
    
    if not result or result.strip() == "":
        return f"Trigger {params.uuid} updated successfully."
    
    return result


@mcp.tool(
    name="btt_delete_trigger",
    annotations={
        "title": "Delete Trigger",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def btt_delete_trigger(params: DeleteTriggerInput) -> str:
    """Delete a trigger from BetterTouchTool.
    
    WARNING: This permanently removes the trigger. Make sure you have
    the correct UUID before deleting.
    
    Args:
        params: Contains the UUID of the trigger to delete.
    
    Returns:
        Confirmation of deletion.
    """
    result = await _btt_request('delete_trigger', {'uuid': params.uuid}, params.connection)
    
    if not result or result.strip() == "":
        return f"Trigger {params.uuid} deleted successfully."
    
    return result


@mcp.tool(
    name="btt_get_variable",
    annotations={
        "title": "Get BTT Variable",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_get_variable(params: GetVariableInput) -> str:
    """Get the value of a BTT variable.
    
    BTT has many built-in variables (like BTTActiveAppBundleIdentifier)
    and supports user-defined variables.
    
    Args:
        params: Variable name and type (string or number).
    
    Returns:
        Current value of the variable.
    """
    endpoint = 'get_string_variable' if params.variable_type == 'string' else 'get_number_variable'
    result = await _btt_request(endpoint, {'variableName': params.variable_name}, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return f"**{params.variable_name}** = `{result}`"


@mcp.tool(
    name="btt_set_variable",
    annotations={
        "title": "Set BTT Variable",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_set_variable(params: SetVariableInput) -> str:
    """Set a BTT variable to a specified value.
    
    Variables can be persistent (survive BTT restart) or runtime-only.
    
    Args:
        params: Variable name, value, type, and persistence setting.
    
    Returns:
        Confirmation of variable being set.
    """
    if params.variable_type == 'string':
        endpoint = 'set_persistent_string_variable' if params.persistent else 'set_string_variable'
    else:
        endpoint = 'set_persistent_number_variable' if params.persistent else 'set_number_variable'
    
    request_params = {
        'variableName': params.variable_name,
        'to': params.value
    }
    
    result = await _btt_request(endpoint, request_params, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    persistence = "persistent " if params.persistent else ""
    return f"Set {persistence}variable **{params.variable_name}** to `{params.value}`"


@mcp.tool(
    name="btt_update_widget",
    annotations={
        "title": "Update Widget",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_update_widget(params: UpdateWidgetInput) -> str:
    """Update the display of a Touch Bar, Menubar, or Stream Deck widget.
    
    This allows temporary updates to widget appearance without changing
    the underlying configuration.
    
    Args:
        params: Widget UUID, type, and display properties to update.
    
    Returns:
        Confirmation of widget update.
    """
    endpoint_map = {
        'touch_bar': 'update_touch_bar_widget',
        'menubar': 'update_menubar_item',
        'stream_deck': 'update_stream_deck_widget'
    }
    
    endpoint = endpoint_map.get(params.widget_type, 'update_touch_bar_widget')
    
    request_params = {'uuid': params.uuid}
    if params.text:
        request_params['text'] = params.text
    if params.icon_path:
        request_params['icon_path'] = params.icon_path
    if params.icon_data:
        request_params['icon_data'] = params.icon_data
    if params.background_color:
        request_params['background_color'] = params.background_color
    
    result = await _btt_request(endpoint, request_params, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return f"Widget {params.uuid} updated successfully."


@mcp.tool(
    name="btt_refresh_widget",
    annotations={
        "title": "Refresh Widget",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_refresh_widget(params: RefreshWidgetInput) -> str:
    """Refresh a script widget to re-execute its scripts.
    
    Use this to force a widget to update its display by running
    its assigned scripts again.
    
    Args:
        params: UUID of the widget to refresh.
    
    Returns:
        Confirmation of refresh.
    """
    result = await _btt_request('refresh_widget', {'uuid': params.uuid}, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return f"Widget {params.uuid} refreshed."


@mcp.tool(
    name="btt_get_clipboard",
    annotations={
        "title": "Get Clipboard Content",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_get_clipboard(params: GetClipboardInput) -> str:
    """Get the current clipboard content.
    
    Can retrieve content in various formats including plain text, HTML,
    images (as base64), and more.
    
    Args:
        params: Format to retrieve and whether to return as base64.
    
    Returns:
        Clipboard content.
    """
    request_params = {
        'format': params.format,
        'asBase64': 'true' if params.as_base64 else 'false'
    }
    
    result = await _btt_request('get_clipboard_content', request_params, params.connection)
    return result


@mcp.tool(
    name="btt_set_clipboard",
    annotations={
        "title": "Set Clipboard Content",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_set_clipboard(params: SetClipboardInput) -> str:
    """Set the clipboard content.
    
    Can set content in various formats including plain text and HTML.
    
    Args:
        params: Content to set and format.
    
    Returns:
        Confirmation of clipboard being set.
    """
    request_params = {
        'content': params.content,
        'format': params.format
    }
    
    result = await _btt_request('set_clipboard_content', request_params, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return "Clipboard content set successfully."


@mcp.tool(
    name="btt_export_preset",
    annotations={
        "title": "Export Preset",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_export_preset(params: ExportPresetInput) -> str:
    """Export a BTT preset to a file.
    
    Useful for backing up configurations or sharing presets.
    
    Args:
        params: Preset name and export options.
    
    Returns:
        Path to exported preset file.
    """
    request_params = {
        'name': params.name,
        'outputPath': params.output_path,
        'compress': '1' if params.compress else '0',
        'includeSettings': '1' if params.include_settings else '0'
    }
    
    result = await _btt_request('export_preset', request_params, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return f"Preset '{params.name}' exported to {params.output_path}"


@mcp.tool(
    name="btt_import_preset",
    annotations={
        "title": "Import Preset",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def btt_import_preset(params: ImportPresetInput) -> str:
    """Import a BTT preset from a file.
    
    Args:
        params: Path to the preset file.
    
    Returns:
        Confirmation of import.
    """
    result = await _btt_request('import_preset', {'path': params.path}, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return f"Preset imported from {params.path}"


@mcp.tool(
    name="btt_get_preset_details",
    annotations={
        "title": "Get Preset Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def btt_get_preset_details(params: GetPresetDetailsInput) -> str:
    """Get details about a specific preset.
    
    Returns information about the preset's status, UUID, and visibility.
    
    Args:
        params: Name of the preset to query.
    
    Returns:
        Preset details in markdown or JSON format.
    """
    result = await _btt_request('get_preset_details', {'name': params.name}, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    if params.response_format == ResponseFormat.JSON:
        return result
    
    try:
        preset_data = json.loads(result)
        return _format_preset_details(preset_data)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_display_notification",
    annotations={
        "title": "Display Notification",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def btt_display_notification(params: DisplayNotificationInput) -> str:
    """Display a macOS notification via BTT.
    
    Args:
        params: Notification title, subtitle, sound, and optional image.
    
    Returns:
        Confirmation of notification being displayed.
    """
    request_params = {'title': params.title}
    
    if params.subtitle:
        request_params['subTitle'] = params.subtitle
    if params.sound_name:
        request_params['soundName'] = params.sound_name
    if params.image_path:
        request_params['imagePath'] = params.image_path
    
    result = await _btt_request('display_notification', request_params, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return "Notification displayed."


@mcp.tool(
    name="btt_reveal_in_ui",
    annotations={
        "title": "Reveal Element in BTT UI",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def btt_reveal_in_ui(params: RevealElementInput) -> str:
    """Reveal a trigger or element in the BetterTouchTool UI.
    
    Opens BTT and navigates to the specified element for editing.
    
    Args:
        params: UUID of the element to reveal.
    
    Returns:
        Confirmation.
    """
    result = await _btt_request('reveal_element_in_ui', {'uuid': params.uuid}, params.connection)
    
    if result.startswith("Error:"):
        return result
    
    return f"Element {params.uuid} revealed in BTT UI."


# =============================================================================
# Server Entry Point
# =============================================================================

def main():
    """Run the BetterTouchTool MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
