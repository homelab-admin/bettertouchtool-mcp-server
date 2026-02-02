"""
MCP Server initialization and entry point.
"""

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server - this is imported by tool modules
mcp = FastMCP("btt_mcp")


def main():
    """Run the BetterTouchTool MCP server."""
    # Import tools to register them with the MCP server
    # This must happen before mcp.run()
    import btt_mcp.tools  # noqa: F401

    mcp.run()


if __name__ == "__main__":
    main()
