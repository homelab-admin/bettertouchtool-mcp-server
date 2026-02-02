"""
CLI client for bttcli communication.
"""

import subprocess
from typing import Any

from btt_mcp.config import get_bttcli_path


def cli_request(method: str, params: dict[str, Any]) -> str:
    """Make a request using bttcli.

    Args:
        method: The BTT method to call
        params: Parameters to pass to the method

    Returns:
        Command output or error message
    """
    cli_path = get_bttcli_path()
    if not cli_path:
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
