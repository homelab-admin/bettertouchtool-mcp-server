"""
Common models shared across all BTT MCP tools.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.config import DEFAULT_BTT_HOST, DEFAULT_BTT_PORT


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


class BTTConnectionConfig(BaseModel):
    """Configuration for connecting to BetterTouchTool."""

    model_config = ConfigDict(str_strip_whitespace=True)

    host: str = Field(
        default=DEFAULT_BTT_HOST,
        description="BTT webserver host (default: 127.0.0.1)",
    )
    port: int = Field(
        default=DEFAULT_BTT_PORT,
        description="BTT webserver port (default: 12345)",
        ge=1,
        le=65535,
    )
    shared_secret: Optional[str] = Field(
        default=None,
        description="Shared secret for BTT webserver authentication (if configured)",
    )
    use_cli: bool = Field(
        default=False,
        description="Use bttcli instead of HTTP (faster, uses Unix socket)",
    )
