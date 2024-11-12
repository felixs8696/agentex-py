from enum import Enum
from typing import Optional

from pydantic import Field

from agentex.utils.model_utils import BaseModel


class AgentStatus(str, Enum):
    PENDING = "Pending"
    BUILDING = "Building"
    READY = "Ready"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class Agent(BaseModel):
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
    workflow_name: str = Field(
        ...,
        description="The name of the workflow that defines the agent."
    )
    workflow_queue_name: str = Field(
        ...,
        description="The name of the queue to send tasks to."
    )
