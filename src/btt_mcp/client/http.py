"""
HTTP client for BTT webserver communication.
"""

import urllib.parse
from typing import Any

import httpx

from btt_mcp.models.common import BTTConnectionConfig


def build_url(
    endpoint: str,
    params: dict[str, Any],
    config: BTTConnectionConfig,
) -> str:
    """Build the BTT webserver URL with parameters.

    Args:
        endpoint: The BTT API endpoint (e.g., 'get_triggers')
        params: Query parameters to include
        config: BTT connection configuration

    Returns:
        Fully constructed URL with query string
    """
    base_url = f"http://{config.host}:{config.port}/{endpoint}/"

    # Add shared secret if configured
    if config.shared_secret:
        params["shared_secret"] = config.shared_secret

    # Filter out None values and encode parameters
    filtered_params = {k: v for k, v in params.items() if v is not None}

    if filtered_params:
        query_string = urllib.parse.urlencode(
            filtered_params, quote_via=urllib.parse.quote
        )
        return f"{base_url}?{query_string}"

    return base_url


async def http_request(
    endpoint: str,
    params: dict[str, Any],
    config: BTTConnectionConfig,
) -> str:
    """Make an HTTP request to the BTT webserver.

    Args:
        endpoint: The BTT API endpoint
        params: Query parameters
        config: BTT connection configuration

    Returns:
        Response text from BTT, or error message
    """
    url = build_url(endpoint, params, config)

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
            return (
                f"Error: Could not connect to BTT webserver at {config.host}:{config.port}. "
                "Is the webserver enabled in BTT preferences?"
            )
        except httpx.TimeoutException:
            return "Error: Request timed out. BTT may be busy or unresponsive."
