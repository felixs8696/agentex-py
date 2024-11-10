from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Optional, TypeVar, Any

from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.client.types.tasks import UserMessage
from agentex.constants import DEFAULT_ROOT_THREAD_NAME
from agentex.sdk.execution.helpers import WorkflowHelper
from agentex.sdk.lib.activities.names import ActivityName
from agentex.sdk.lib.activities.state import AppendMessagesToThreadParams
from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel

logger = make_logger(__name__)

T = TypeVar("T", bound="BaseModel")


class AgentStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"


class AgentTaskWorkflowParams(BaseModel):
    task: Task
    agent: Agent
    require_approval: Optional[bool] = False


class HumanInstruction(BaseModel):
    task_id: str
    prompt: str
    thread_name: str = DEFAULT_ROOT_THREAD_NAME


class BaseWorkflow(ABC):

    def __init__(self):
        self.waiting_for_instruction = False
        self.task_approved = False
        self.status = AgentStatus.IDLE

    def set_status(self, status: AgentStatus):
        self.status = status

    @workflow.signal
    async def instruct(self, instruction: HumanInstruction) -> None:
        await WorkflowHelper.execute_activity(
            activity_name=ActivityName.APPEND_MESSAGES_TO_THREAD,
            arg=AppendMessagesToThreadParams(
                task_id=instruction.task_id,
                thread_name=instruction.thread_name,
                messages=[UserMessage(content=instruction.prompt)]
            ),
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )
        self.waiting_for_instruction = False

    @workflow.signal
    async def approve(self, _: Optional[Any] = None) -> None:
        self.task_approved = True

    @abstractmethod
    async def run(self, params: AgentTaskWorkflowParams):
        raise NotImplementedError
