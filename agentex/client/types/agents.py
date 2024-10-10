from typing import Dict, Any, List

from pydantic import Field, field_validator

from agentex.utils.json_schema import validate_payload
from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel

logger = make_logger(__name__)


class CreateActionRequest(BaseModel):
    name: str = Field(
        ...,
        description="The name of the action."
    )
    description: str = Field(
        ...,
        description="The description of the action."
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="The JSON schema describing the parameters that the action takes in"
    )
    test_payload: Dict[str, Any] = Field(
        ...,
        description="The payload to use when testing the action."
    )
    version: str = Field(
        ...,
        description="The version of the action."
    )


class CreateAgentRequest(BaseModel):
    name: str = Field(
        ...,
        title="The unique name of the agent",
        pattern=r"^[a-zA-Z0-9-]+$",
    )
    description: str = Field(
        ...,
        title="The description of what the agent does",
    )
    version: str = Field(
        ...,
        title="The version of the agent",
        pattern=r"^[a-zA-Z0-9-\.]+$",
    )
    model: str = Field(
        ...,
        description="The LLM model powering the agent."
    )
    instructions: str = Field(
        ...,
        title="The initial instructions to give to the agent",
    )
    actions: List[CreateActionRequest] = Field(
        ...,
        title="The list of actions that the agent can perform",
    )

    @classmethod
    @field_validator('actions')
    def validate_x(cls, actions: List[CreateActionRequest]) -> List[CreateActionRequest]:
        for action in actions:
            validate_payload(json_schema=action.parameters, payload=action.test_payload)
        return actions


class CreateAgentResponse(BaseModel):
    id: str = Field(
        ...,
        description="The unique identifier of the agent."
    )
    name: str = Field(
        ...,
        description="The unique name of the agent."
    )
