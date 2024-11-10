from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Optional, TypeVar, Any, List, Dict

from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.client.types.tasks import UserMessage
from agentex.constants import DEFAULT_ROOT_THREAD_NAME
from agentex.sdk.execution.helpers import WorkflowHelper
from agentex.sdk.lib.activities.names import ActivityName
from agentex.sdk.lib.activities.state import AppendMessagesToThreadParams
from agentex.src.entities.task import Task
from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel

logger = make_logger(__name__)

T = TypeVar("T", bound="BaseModel")


class ExecutionStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"


class AgentTaskWorkflowParams(BaseModel):
    task: Task
    require_approval: Optional[bool] = False


class HumanInstruction(BaseModel):
    task_id: str
    prompt: str
    thread_name: str = DEFAULT_ROOT_THREAD_NAME


class BaseWorkflow(ABC):

    def __init__(
        self,
        model: str,
        version: str,
        name: str,
        description: str,
        instructions: str,
    ):
        self.name = name
        self.description = description
        self.model = model
        self.version = version
        self.instructions = instructions

        self.waiting_for_instruction = False
        self.task_approved = False
        self.event_log: List[Dict[str, Any]] = []

    @workflow.query
    async def get_event_log(self) -> List[Dict[str, Any]]:
        return self.event_log

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
        self.event_log.append({"event": "human_instruction_received", "instruction": instruction})
        self.waiting_for_instruction = False

    @workflow.signal
    async def approve(self, _: Optional[Any] = None) -> None:
        self.event_log.append({"event": "task_approved"})
        self.task_approved = True

    @abstractmethod
    async def run(self, params: AgentTaskWorkflowParams):
        raise NotImplementedError
