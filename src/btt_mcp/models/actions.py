"""
Action-related input models for triggering BTT actions.
"""

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.models.common import BTTConnectionConfig


class TriggerNamedInput(BaseModel):
    """Input for triggering a named trigger."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    trigger_name: str = Field(
        ...,
        description="Name of the named trigger to execute",
        min_length=1,
    )
    wait_for_reply: bool = Field(
        default=True,
        description="Wait for the trigger to complete and return result",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class TriggerActionInput(BaseModel):
    """Input for triggering a BTT action via JSON definition."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    action_json: str = Field(
        ...,
        description="JSON definition of the action to trigger (copy from BTT via right-click -> Copy JSON)",
    )
    wait_for_reply: bool = Field(
        default=False,
        description="Wait for the action to complete",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )
