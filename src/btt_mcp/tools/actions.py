"""
Action triggering tools.
"""

from btt_mcp.client import btt_request
from btt_mcp.models import TriggerActionInput, TriggerNamedInput
from btt_mcp.server import mcp


@mcp.tool(
    name="btt_trigger_named",
    annotations={
        "title": "Trigger Named Action",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
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
        "trigger_name": params.trigger_name,
        "wait_for_reply": "true" if params.wait_for_reply else "false",
    }

    result = await btt_request("trigger_named", request_params, params.connection)

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
        "openWorldHint": True,
    },
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
    result = await btt_request(
        "trigger_action", {"json": params.action_json}, params.connection
    )

    if not result or result.strip() == "":
        return "Action triggered successfully."

    return result
