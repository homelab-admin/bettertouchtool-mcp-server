"""
Variable management tools.
"""

from btt_mcp.client import btt_request
from btt_mcp.models import GetVariableInput, SetVariableInput
from btt_mcp.server import mcp


@mcp.tool(
    name="btt_get_variable",
    annotations={
        "title": "Get BTT Variable",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
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
    endpoint = (
        "get_string_variable"
        if params.variable_type == "string"
        else "get_number_variable"
    )
    result = await btt_request(
        endpoint, {"variableName": params.variable_name}, params.connection
    )

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
        "openWorldHint": False,
    },
)
async def btt_set_variable(params: SetVariableInput) -> str:
    """Set a BTT variable to a specified value.

    Variables can be persistent (survive BTT restart) or runtime-only.

    Args:
        params: Variable name, value, type, and persistence setting.

    Returns:
        Confirmation of variable being set.
    """
    if params.variable_type == "string":
        endpoint = (
            "set_persistent_string_variable"
            if params.persistent
            else "set_string_variable"
        )
    else:
        endpoint = (
            "set_persistent_number_variable"
            if params.persistent
            else "set_number_variable"
        )

    request_params = {"variableName": params.variable_name, "to": params.value}

    result = await btt_request(endpoint, request_params, params.connection)

    if result.startswith("Error:"):
        return result

    persistence = "persistent " if params.persistent else ""
    return f"Set {persistence}variable **{params.variable_name}** to `{params.value}`"
