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
    workflow_name: str = Field(
        ...,
        description="The name of the workflow that defines the agent."
    )
    workflow_queue_name: str = Field(
        ...,
        description="The name of the queue to send tasks to."
    )


class AgentStatus(str, Enum):
    PENDING = "Pending"
    BUILDING = "Building"
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
    status: AgentStatus = Field(
        AgentStatus.UNKNOWN,
        description="The status of the action, indicating if it's building, ready, failed, etc."
    )
    status_reason: Optional[str] = Field(
        None,
        description="The reason for the status of the action."
    )
