"""
Tests for BTT MCP imports and structure.
"""



class TestImports:
    """Test that all modules can be imported."""

    def test_main_import(self):
        from btt_mcp import main

        assert callable(main)

    def test_server_import(self):
        from btt_mcp.server import mcp

        assert mcp is not None

    def test_config_import(self):
        from btt_mcp.config import (
            DEFAULT_BTT_HOST,
            DEFAULT_BTT_PORT,
        )

        assert DEFAULT_BTT_HOST == "127.0.0.1"
        assert DEFAULT_BTT_PORT == 12345

    def test_models_import(self):
        from btt_mcp.models import (
            BTTConnectionConfig,
        )

        assert BTTConnectionConfig is not None

    def test_client_import(self):
        from btt_mcp.client import btt_request, cli_request, http_request

        assert callable(btt_request)
        assert callable(http_request)
        assert callable(cli_request)

    def test_formatters_import(self):
        from btt_mcp.formatters import (
            format_trigger,
        )

        assert callable(format_trigger)

    def test_tools_import(self):
        from btt_mcp.tools import actions, triggers

        assert triggers is not None
        assert actions is not None


class TestToolRegistration:
    """Test that tools are properly registered with MCP."""

    def test_tools_registered(self):
        # Import tools to register them
        import btt_mcp.tools  # noqa: F401
        from btt_mcp.server import mcp

        # FastMCP stores tools internally - we just verify no errors on import
        assert mcp is not None
