"""
Tests for BTT MCP client utilities.
"""


from btt_mcp.client.http import build_url
from btt_mcp.config import NAMED_TRIGGER_ID, TRIGGER_TYPES, get_bttcli_path
from btt_mcp.models import BTTConnectionConfig


class TestBuildUrl:
    """Tests for URL building."""

    def test_basic_url(self):
        config = BTTConnectionConfig()
        url = build_url("get_triggers", {}, config)
        assert url == "http://127.0.0.1:56786/get_triggers/"

    def test_url_with_params(self):
        config = BTTConnectionConfig()
        url = build_url("get_triggers", {"trigger_id": 643}, config)
        assert url == "http://127.0.0.1:56786/get_triggers/?trigger_id=643"

    def test_url_with_shared_secret(self):
        config = BTTConnectionConfig(shared_secret="secret123")
        url = build_url("get_triggers", {}, config)
        assert "shared_secret=secret123" in url

    def test_url_filters_none_values(self):
        config = BTTConnectionConfig()
        url = build_url("get_triggers", {"param1": "value", "param2": None}, config)
        assert "param1=value" in url
        assert "param2" not in url

    def test_custom_host_port(self):
        config = BTTConnectionConfig(host="192.168.1.1", port=9999)
        url = build_url("test", {}, config)
        assert url == "http://192.168.1.1:9999/test/"


class TestConfig:
    """Tests for config constants."""

    def test_trigger_types(self):
        assert "keyboard_shortcut" in TRIGGER_TYPES
        assert TRIGGER_TYPES["keyboard_shortcut"] == "BTTTriggerTypeKeyboardShortcut"
        assert TRIGGER_TYPES["named"] == "BTTTriggerTypeOtherTriggers"

    def test_named_trigger_id(self):
        assert NAMED_TRIGGER_ID == 643

    def test_get_bttcli_path(self):
        # This may return None if BTT is not installed
        path = get_bttcli_path()
        assert path is None or path.endswith("bttcli")
