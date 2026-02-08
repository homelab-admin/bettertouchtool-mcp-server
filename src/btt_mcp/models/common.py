"""
Common models shared across all BTT MCP tools.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.config import (
    get_default_host,
    get_default_port,
    get_default_shared_secret,
    get_default_use_cli,
)

# Use Literal instead of Enum to avoid $ref in JSON schema.
# VS Code Copilot cannot resolve $ref references in tool parameter schemas,
# which causes tool invocations to silently fail.
# See: https://github.com/microsoft/vscode/issues/286179
ResponseFormat = Literal["markdown", "json"]


class BTTConnectionConfig(BaseModel):
    """Configuration for connecting to BetterTouchTool.

    Defaults are loaded from ~/.config/btt-mcp/config.yml if it exists.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    host: str = Field(
        default_factory=get_default_host,
        description="BTT webserver host (default: 127.0.0.1)",
    )
    port: int = Field(
        default_factory=get_default_port,
        description="BTT webserver port (default: 56786)",
        ge=1,
        le=65535,
    )
    shared_secret: Optional[str] = Field(
        default_factory=get_default_shared_secret,
        description="Shared secret for BTT webserver authentication (if configured)",
    )
    use_cli: bool = Field(
        default_factory=get_default_use_cli,
        description="Use bttcli instead of HTTP (faster, uses Unix socket)",
    )
