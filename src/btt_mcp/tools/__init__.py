"""
MCP tool implementations for BTT.

Each module registers its tools with the shared MCP server instance.
"""

from btt_mcp.tools import (
    actions,
    clipboard,
    floating_menus,
    presets,
    reference,
    triggers,
    variables,
    widgets,
)

__all__ = [
    "triggers",
    "actions",
    "variables",
    "widgets",
    "clipboard",
    "presets",
    "floating_menus",
    "reference",
]
