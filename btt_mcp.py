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

import sys
from pathlib import Path

# Add src to path to import btt_mcp package
sys.path.insert(0, str(Path(__file__).parent / "src"))

from btt_mcp import main

if __name__ == "__main__":
    main()
