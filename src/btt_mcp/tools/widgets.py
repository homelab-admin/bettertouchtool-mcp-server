"""
Widget management tools (Touch Bar, Menubar, Stream Deck).
"""

from btt_mcp.client import btt_request
from btt_mcp.config import WIDGET_ENDPOINT_MAP
from btt_mcp.models import RefreshWidgetInput, UpdateWidgetInput
from btt_mcp.server import mcp


@mcp.tool(
    name="btt_update_widget",
    annotations={
        "title": "Update Widget",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
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
    endpoint = WIDGET_ENDPOINT_MAP.get(params.widget_type, "update_touch_bar_widget")

    request_params = {"uuid": params.uuid}
    if params.text:
        request_params["text"] = params.text
    if params.icon_path:
        request_params["icon_path"] = params.icon_path
    if params.icon_data:
        request_params["icon_data"] = params.icon_data
    if params.background_color:
        request_params["background_color"] = params.background_color

    result = await btt_request(endpoint, request_params, params.connection)

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
        "openWorldHint": False,
    },
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
    result = await btt_request(
        "refresh_widget", {"uuid": params.uuid}, params.connection
    )

    if result.startswith("Error:"):
        return result

    return f"Widget {params.uuid} refreshed."
