from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import Field

from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel

logger = make_logger(__name__)


class CreateAgentRequest(BaseModel):
    name: str = Field(
        ...,
        description="The unique name of the agent."
    )
    description: str = Field(
        ...,
        description="The description of the agent."
    )
    version: str = Field(
        ...,
        description="The version of the agent."
    )
    action_service_port: int = Field(
        ...,
        description="The port on which the service will run inside the container. This is the port that the "
                    "command is pointing at in your Dockerfile. It should be specified in the action manifest."
    )


class ActionSchemaModel(BaseModel):
    name: str = Field(
        ...,
        description="The name of the action. If you try to create a new action with the same name as an existing "
                    "action, the the version must be changed to create a new version of the action."
    )
    description: str = Field(
        ...,
        description="The description of the action."
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="The JSON schema describing the parameters that the action takes in"
    )


class ActionModel(BaseModel):
    """
    Every Agent server will expose a REST API at the root route that will allow Agentex to fetch the agent's metadata.
    This includes a list of actions that the agent can perform which are defined by this spec.
    """
    schema: ActionSchemaModel = Field(
        ...,
        description="The JSON schema describing the parameters that the action takes in"
    )
    test_payload: Optional[Dict[str, Any]] = Field(
        None,
        description="The payload to use when testing the action."
    )


class AgentStatus(str, Enum):
    PENDING = "Pending"
    BUILDING = "Building"
    IDLE = "Idle"
    ACTIVE = "Active"
    READY = "Ready"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class AgentModel(BaseModel):
    id: str = Field(
        ...,
        description="The unique identifier of the agent."
    )
    name: str = Field(
        ...,
        description="The unique name of the agent."
    )
    description: str = Field(
        ...,
        description="The description of the action."
    )
    version: str = Field(
        ...,
        description="The version of the action."
    )
    model: Optional[str] = Field(
        None,
        description="The LLM model powering the agent."
    )
    instructions: Optional[str] = Field(
        None,
        description="The instructions for the agent."
    )
    actions: Optional[List[ActionModel]] = Field(
        default=None,
        description="The actions that the agent can perform."
    )
    status: AgentStatus = Field(
        AgentStatus.UNKNOWN,
        description="The status of the action, indicating if it's building, ready, failed, etc."
    )
    status_reason: Optional[str] = Field(
        None,
        description="The reason for the status of the action."
    )
