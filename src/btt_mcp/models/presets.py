"""
Preset, notification, and UI-related input models.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.models.common import BTTConnectionConfig, ResponseFormat


class ExportPresetInput(BaseModel):
    """Input for exporting a preset."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(
        ...,
        description="Name of the preset to export",
        min_length=1,
    )
    output_path: str = Field(
        ...,
        description="Path where the preset file should be saved",
    )
    compress: bool = Field(
        default=True,
        description="Compress the exported preset",
    )
    include_settings: bool = Field(
        default=False,
        description="Include BTT settings in export",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class ImportPresetInput(BaseModel):
    """Input for importing a preset."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(
        ...,
        description="Path to the preset file to import",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class GetPresetDetailsInput(BaseModel):
    """Input for getting preset details."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(
        ...,
        description="Name of the preset to query",
        min_length=1,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for raw data",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class DisplayNotificationInput(BaseModel):
    """Input for displaying a notification."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(
        ...,
        description="Notification title",
        min_length=1,
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="Notification subtitle",
    )
    sound_name: Optional[str] = Field(
        default=None,
        description="Name of sound to play (e.g., 'frog', 'Ping')",
    )
    image_path: Optional[str] = Field(
        default=None,
        description="Path to image to display in notification",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class RevealElementInput(BaseModel):
    """Input for revealing an element in BTT UI."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the element to reveal in BTT UI",
        min_length=36,
        max_length=36,
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )
