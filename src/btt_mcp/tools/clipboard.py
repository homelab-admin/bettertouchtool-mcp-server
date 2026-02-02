"""
Clipboard management tools.
"""

from btt_mcp.client import btt_request
from btt_mcp.models import GetClipboardInput, SetClipboardInput
from btt_mcp.server import mcp


@mcp.tool(
    name="btt_get_clipboard",
    annotations={
        "title": "Get Clipboard Content",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
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
        "format": params.format,
        "asBase64": "true" if params.as_base64 else "false",
    }

    result = await btt_request("get_clipboard_content", request_params, params.connection)
    return result


@mcp.tool(
    name="btt_set_clipboard",
    annotations={
        "title": "Set Clipboard Content",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_set_clipboard(params: SetClipboardInput) -> str:
    """Set the clipboard content.

    Can set content in various formats including plain text and HTML.

    Args:
        params: Content to set and format.

    Returns:
        Confirmation of clipboard being set.
    """
    request_params = {"content": params.content, "format": params.format}

    result = await btt_request("set_clipboard_content", request_params, params.connection)

    if result.startswith("Error:"):
        return result

    return "Clipboard content set successfully."
