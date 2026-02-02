"""
Base request dispatcher for BTT communication.
"""

from typing import Any

from btt_mcp.client.cli import cli_request
from btt_mcp.client.http import http_request
from btt_mcp.models.common import BTTConnectionConfig


async def btt_request(
    endpoint: str,
    params: dict[str, Any],
    config: BTTConnectionConfig,
) -> str:
    """Make a request to BTT using configured method (HTTP or CLI).

    This is the main entry point for all BTT communication. It dispatches
    to either the HTTP client or CLI based on the configuration.

    Args:
        endpoint: The BTT API endpoint
        params: Request parameters
        config: BTT connection configuration

    Returns:
        Response from BTT
    """
    if config.use_cli:
        return cli_request(endpoint, params)
    return await http_request(endpoint, params, config)
