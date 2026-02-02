#!/usr/bin/env python3
"""
BetterTouchTool MCP Server - Legacy Entry Point

This file is kept for backwards compatibility only.
The actual implementation is in src/btt_mcp/

Usage:
    python btt_mcp.py
    # or
    btt-mcp-server
"""

from btt_mcp import main

if __name__ == "__main__":
    main()
