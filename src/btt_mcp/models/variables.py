"""
Variable-related input models.
"""

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.models.common import BTTConnectionConfig


class GetVariableInput(BaseModel):
    """Input for getting a BTT variable."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    variable_name: str = Field(
        ...,
        description="Name of the variable to retrieve",
        min_length=1,
    )
    variable_type: str = Field(
        default="string",
        description="Type of variable: 'string' or 'number'",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class SetVariableInput(BaseModel):
    """Input for setting a BTT variable."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    variable_name: str = Field(
        ...,
        description="Name of the variable to set",
        min_length=1,
    )
    value: str = Field(
        ...,
        description="Value to set (will be converted to number if variable_type is 'number')",
    )
    variable_type: str = Field(
        default="string",
        description="Type of variable: 'string' or 'number'",
    )
    persistent: bool = Field(
        default=False,
        description="If True, variable persists across BTT restarts",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )
