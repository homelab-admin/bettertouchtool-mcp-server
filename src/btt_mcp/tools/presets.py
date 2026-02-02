"""
Preset, notification, and UI tools.
"""

import json

from btt_mcp.client import btt_request
from btt_mcp.formatters import format_preset_details
from btt_mcp.models import (
    DisplayNotificationInput,
    ExportPresetInput,
    GetPresetDetailsInput,
    ImportPresetInput,
    ResponseFormat,
    RevealElementInput,
)
from btt_mcp.server import mcp


@mcp.tool(
    name="btt_export_preset",
    annotations={
        "title": "Export Preset",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
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
        "name": params.name,
        "outputPath": params.output_path,
        "compress": "1" if params.compress else "0",
        "includeSettings": "1" if params.include_settings else "0",
    }

    result = await btt_request("export_preset", request_params, params.connection)

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
        "openWorldHint": False,
    },
)
async def btt_import_preset(params: ImportPresetInput) -> str:
    """Import a BTT preset from a file.

    Args:
        params: Path to the preset file.

    Returns:
        Confirmation of import.
    """
    result = await btt_request(
        "import_preset", {"path": params.path}, params.connection
    )

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
        "openWorldHint": False,
    },
)
async def btt_get_preset_details(params: GetPresetDetailsInput) -> str:
    """Get details about a specific preset.

    Returns information about the preset's status, UUID, and visibility.

    Args:
        params: Name of the preset to query.

    Returns:
        Preset details in markdown or JSON format.
    """
    result = await btt_request(
        "get_preset_details", {"name": params.name}, params.connection
    )

    if result.startswith("Error:"):
        return result

    if params.response_format == ResponseFormat.JSON:
        return result

    try:
        preset_data = json.loads(result)
        return format_preset_details(preset_data)
    except json.JSONDecodeError:
        return f"Error parsing response: {result}"


@mcp.tool(
    name="btt_display_notification",
    annotations={
        "title": "Display Notification",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def btt_display_notification(params: DisplayNotificationInput) -> str:
    """Display a macOS notification via BTT.

    Args:
        params: Notification title, subtitle, sound, and optional image.

    Returns:
        Confirmation of notification being displayed.
    """
    request_params = {"title": params.title}

    if params.subtitle:
        request_params["subTitle"] = params.subtitle
    if params.sound_name:
        request_params["soundName"] = params.sound_name
    if params.image_path:
        request_params["imagePath"] = params.image_path

    result = await btt_request(
        "display_notification", request_params, params.connection
    )

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
        "openWorldHint": True,
    },
)
async def btt_reveal_in_ui(params: RevealElementInput) -> str:
    """Reveal a trigger or element in the BetterTouchTool UI.

    Opens BTT and navigates to the specified element for editing.

    Args:
        params: UUID of the element to reveal.

    Returns:
        Confirmation.
    """
    result = await btt_request(
        "reveal_element_in_ui", {"uuid": params.uuid}, params.connection
    )

    if result.startswith("Error:"):
        return result

    return f"Element {params.uuid} revealed in BTT UI."
