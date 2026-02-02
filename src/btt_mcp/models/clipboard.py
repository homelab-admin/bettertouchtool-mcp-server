"""
Clipboard-related input models.
"""

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.models.common import BTTConnectionConfig


class GetClipboardInput(BaseModel):
    """Input for getting clipboard content."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    format: str = Field(
        default="NSPasteboardTypeString",
        description="Clipboard format (e.g., 'NSPasteboardTypeString', 'NSPasteboardTypeHTML', 'all')",
    )
    as_base64: bool = Field(
        default=False,
        description="Return content as base64 encoded",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class SetClipboardInput(BaseModel):
    """Input for setting clipboard content."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    content: str = Field(
        ...,
        description="Content to put in clipboard",
    )
    format: str = Field(
        default="NSPasteboardTypeString",
        description="Clipboard format (e.g., 'NSPasteboardTypeString', 'NSPasteboardTypeHTML')",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )
