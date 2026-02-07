"""
MCP Server initialization and entry point.
"""

import json
import os
import sys

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server - this is imported by tool modules
mcp = FastMCP("btt_mcp")

# Debug mode: set BTT_MCP_DEBUG=1 to log raw tool call arguments to stderr
_DEBUG = os.environ.get("BTT_MCP_DEBUG", "0") == "1"


def main():
    """Run the BetterTouchTool MCP server."""
    # Import tools to register them with the MCP server
    # This must happen before mcp.run()
    import btt_mcp.tools  # noqa: F401

    if _DEBUG:
        _install_debug_logging()

    print("BTT MCP Server starting...", file=sys.stderr)
    if _DEBUG:
        print("DEBUG MODE ENABLED - raw tool arguments will be logged", file=sys.stderr)
    mcp.run()


def _install_debug_logging():
    """Patch the tool manager to log raw arguments before validation."""
    original_call_tool = mcp._tool_manager.call_tool

    async def debug_call_tool(name, arguments, **kwargs):
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"TOOL CALL: {name}", file=sys.stderr)
        print("RAW ARGUMENTS:", file=sys.stderr)
        print(json.dumps(arguments, indent=2, default=str), file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        try:
            result = await original_call_tool(name, arguments, **kwargs)
            print(f"TOOL RESULT (success): {name}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"TOOL ERROR: {name}", file=sys.stderr)
            print(f"  Exception type: {type(e).__name__}", file=sys.stderr)
            print(f"  Exception: {e}", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)
            raise

    mcp._tool_manager.call_tool = debug_call_tool


if __name__ == "__main__":
    main()
