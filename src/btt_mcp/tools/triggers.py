"""
Trigger management tools.
"""

import json

from btt_mcp.client import btt_request
from btt_mcp.config import NAMED_TRIGGER_ID
from btt_mcp.formatters import format_trigger, format_triggers_list
from btt_mcp.models import (
    AddTriggerInput,
    DeleteTriggerInput,
    ExecuteTriggerInput,
    GetTriggerInput,
    GetTriggersInput,
    ListNamedTriggersInput,
    UpdateTriggerInput,
)
from btt_mcp.server import mcp


@mcp.tool(
    name="btt_get_triggers",
    annotations={
        "title": "Get BTT Triggers",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
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
        request_params["trigger_type"] = params.trigger_type
    if params.trigger_id is not None:
        request_params["trigger_id"] = params.trigger_id
    if params.trigger_parent_uuid:
        request_params["trigger_parent_uuid"] = params.trigger_parent_uuid
    if params.trigger_uuid:
        request_params["trigger_uuid"] = params.trigger_uuid
    if params.app_bundle_identifier:
        request_params["trigger_app_bundle_identifier"] = params.app_bundle_identifier

    result = await btt_request("get_triggers", request_params, params.connection)

    if result.startswith("Error:"):
        return result

    if params.response_format == "json":
        return result

    try:
        triggers = json.loads(result)
        if not isinstance(triggers, list):
            triggers = [triggers]
        return format_triggers_list(triggers)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_get_trigger",
    annotations={
        "title": "Get Single BTT Trigger",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
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
    result = await btt_request("get_trigger", {"uuid": params.uuid}, params.connection)

    if result.startswith("Error:"):
        return result

    if params.response_format == "json":
        return result

    try:
        trigger = json.loads(result)
        return format_trigger(trigger)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_list_named_triggers",
    annotations={
        "title": "List Named Triggers",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_list_named_triggers(params: ListNamedTriggersInput) -> str:
    """List all named triggers configured in BetterTouchTool.

    Named triggers are triggers configured in the 'Other' tab that can be
    called by name from scripts or other actions.

    Returns:
        List of named triggers with their names and UUIDs.
    """
    result = await btt_request(
        "get_triggers", {"trigger_id": NAMED_TRIGGER_ID}, params.connection
    )

    if result.startswith("Error:"):
        return result

    if params.response_format == "json":
        return result

    try:
        triggers = json.loads(result)
        if not isinstance(triggers, list):
            triggers = [triggers]
        return format_triggers_list(triggers, "Named Triggers")
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_add_trigger",
    annotations={
        "title": "Add New Trigger",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def btt_add_trigger(params: AddTriggerInput) -> str:
    """Add a new trigger to BetterTouchTool.

    IMPORTANT: Use btt_lookup_reference to get full documentation on trigger types,
    action IDs, and JSON format before constructing trigger_json.

    Every trigger requires BTTTriggerType (int) and BTTTriggerClass (string).
    Actions go in BTTActionsToExecute array with BTTPredefinedActionType.

    Common trigger examples:

    Named trigger (type 643):
      {"BTTTriggerType": 643, "BTTTriggerClass": "BTTTriggerTypeOtherTriggers",
       "BTTTriggerName": "my_trigger_name",
       "BTTActionsToExecute": [{"BTTPredefinedActionType": 49,
       "BTTLaunchPath": "/Applications/Safari.app"}]}

    Keyboard shortcut (type 0):
      {"BTTTriggerType": 0, "BTTTriggerClass": "BTTTriggerTypeKeyboardShortcut",
       "BTTShortcutKeyCode": 49, "BTTShortcutModifierKeys": 1048576,
       "BTTActionsToExecute": [{"BTTPredefinedActionType": 45}]}

    Modifier keys: Cmd=1048576, Opt=524288, Ctrl=262144, Shift=131072, Fn=8388608
    Combine with addition: Cmd+Shift = 1048576 + 131072 = 1179648

    Args:
        params: Contains the trigger JSON definition and optional parent UUID.

    Returns:
        Confirmation of trigger creation.
    """
    request_params = {"json": params.trigger_json}
    if params.parent_uuid:
        request_params["trigger_parent_uuid"] = params.parent_uuid

    result = await btt_request("add_new_trigger", request_params, params.connection)

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
        "openWorldHint": False,
    },
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
    request_params = {"uuid": params.uuid, "json": params.update_json}

    result = await btt_request("update_trigger", request_params, params.connection)

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
        "openWorldHint": False,
    },
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
    result = await btt_request(
        "delete_trigger", {"uuid": params.uuid}, params.connection
    )

    if not result or result.strip() == "":
        return f"Trigger {params.uuid} deleted successfully."

    return result


@mcp.tool(
    name="btt_execute_trigger",
    annotations={
        "title": "Execute Trigger Actions",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def btt_execute_trigger(params: ExecuteTriggerInput) -> str:
    """Execute all actions assigned to a specific trigger by UUID.

    Args:
        params: Contains the UUID of the trigger to execute.

    Returns:
        Result of the execution.
    """
    result = await btt_request(
        "execute_assigned_actions_for_trigger", {"uuid": params.uuid}, params.connection
    )

    if not result or result.strip() == "":
        return f"Executed actions for trigger {params.uuid} successfully."

    return result
