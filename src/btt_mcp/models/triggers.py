"""
Trigger-related input models.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.models.common import BTTConnectionConfig, ResponseFormat


class GetTriggersInput(BaseModel):
    """Input for retrieving triggers from BTT."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    trigger_type: Optional[str] = Field(
        default=None,
        description="Filter by trigger type (e.g., 'BTTTriggerTypeKeyboardShortcut', 'BTTTriggerTypeTouchBar')",
    )
    trigger_id: Optional[int] = Field(
        default=None,
        description="Filter by trigger ID (e.g., 643 for named triggers)",
    )
    trigger_parent_uuid: Optional[str] = Field(
        default=None,
        description="Get triggers within a specific parent group/folder by UUID",
    )
    trigger_uuid: Optional[str] = Field(
        default=None,
        description="Get a specific trigger by UUID",
    )
    app_bundle_identifier: Optional[str] = Field(
        default=None,
        description="Get triggers for a specific app (e.g., 'com.apple.Safari')",
    )
    response_format: ResponseFormat = Field(
        default="markdown",
        description="Output format: 'markdown' for human-readable or 'json' for raw data",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class GetTriggerInput(BaseModel):
    """Input for getting a single trigger by UUID."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the trigger to retrieve",
        min_length=36,
        max_length=36,
    )
    response_format: ResponseFormat = Field(
        default="markdown",
        description="Output format: 'markdown' for human-readable or 'json' for raw data",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class AddTriggerInput(BaseModel):
    """Input for adding a new trigger to BTT."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    trigger_json: str = Field(
        ...,
        description=(
            "JSON definition of the trigger. Must include BTTTriggerType (int) and "
            "BTTTriggerClass (string). For named triggers: BTTTriggerType=643, "
            'BTTTriggerClass="BTTTriggerTypeOtherTriggers", and BTTTriggerName is required. '
            "Actions go in BTTActionsToExecute array. Use btt_lookup_reference for "
            "full trigger type IDs and JSON format documentation."
        ),
    )
    parent_uuid: Optional[str] = Field(
        default=None,
        description="UUID of parent group/folder to add trigger to",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class UpdateTriggerInput(BaseModel):
    """Input for updating an existing trigger."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the trigger to update",
        min_length=36,
        max_length=36,
    )
    update_json: str = Field(
        ...,
        description=(
            "JSON with the properties to update on the trigger. Only include fields "
            "you want to change. Example: to rename a named trigger, provide "
            '{"BTTTriggerName": "new_name"}. Use btt_lookup_reference for field names.'
        ),
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class DeleteTriggerInput(BaseModel):
    """Input for deleting a trigger."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the trigger to delete",
        min_length=36,
        max_length=36,
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class ExecuteTriggerInput(BaseModel):
    """Input for executing all actions assigned to a trigger."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID of the trigger whose actions should be executed",
        min_length=36,
        max_length=36,
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )


class ListNamedTriggersInput(BaseModel):
    """Input for listing all named triggers."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    response_format: ResponseFormat = Field(
        default="markdown",
    )
    connection: BTTConnectionConfig = Field(
        default_factory=BTTConnectionConfig,
        description="BTT connection configuration",
    )
