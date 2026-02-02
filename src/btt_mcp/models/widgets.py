"""
Widget-related input models (Touch Bar, Menubar, Stream Deck).
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.models.common import BTTConnectionConfig


class UpdateWidgetInput(BaseModel):
    """Input for updating a widget (Touch Bar, Menubar, Stream Deck)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the widget to update",
        min_length=36,
        max_length=36,
    )
    widget_type: str = Field(
        default="touch_bar",
        description="Type of widget: 'touch_bar', 'menubar', or 'stream_deck'",
    )
    text: Optional[str] = Field(
        default=None,
        description="New text to display on the widget",
    )
    icon_path: Optional[str] = Field(
        default=None,
        description="Path to icon file to display",
    )
    icon_data: Optional[str] = Field(
        default=None,
        description="Base64-encoded icon data",
    )
    background_color: Optional[str] = Field(
        default=None,
        description="Background color as 'R,G,B,A' (e.g., '200,100,100,255')",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class RefreshWidgetInput(BaseModel):
    """Input for refreshing a script widget."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the widget to refresh",
        min_length=36,
        max_length=36,
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )
