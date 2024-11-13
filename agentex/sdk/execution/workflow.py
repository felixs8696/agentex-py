from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Optional, Any, List, Dict

from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.constants import DEFAULT_ROOT_THREAD_NAME
from agentex.sdk.execution.helpers import WorkflowHelper
from agentex.sdk.execution.names import SignalName, QueryName
from agentex.sdk.lib.activities.names import ActivityName
from agentex.sdk.lib.activities.state import AppendMessagesToThreadParams, GetMessagesFromThreadParams
from agentex.src.entities.agents import Agent
from agentex.src.entities.llm import Message, UserMessage
from agentex.src.entities.notifications import NotificationRequest
from agentex.src.entities.task import Task
from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel

logger = make_logger(__name__)


class ExecutionStatus(str, Enum):
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

    def __init__(
        self,
        display_name: str,
    ):
        self.display_name = display_name

        self.waiting_for_instruction = False
        self.task_approved = False
        self.event_log: List[Dict[str, Any]] = []

    @workflow.query(name=QueryName.GET_EVENT_LOG)
    async def get_event_log(self) -> List[Dict[str, Any]]:
        return self.event_log

    @workflow.signal(name=SignalName.INSTRUCT)
    async def instruct(self, instruction: HumanInstruction) -> None:
        logger.info(f"Received instruction: {instruction}")
        await WorkflowHelper.execute_activity(
            activity_name=ActivityName.APPEND_MESSAGES_TO_THREAD,
            request=AppendMessagesToThreadParams(
                task_id=instruction.task_id,
                thread_name=instruction.thread_name,
                messages=[UserMessage(content=instruction.prompt)]
            ),
            response_type=List[Message],
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )
        self.event_log.append({"event": "human_instruction_received", "instruction": instruction})
        self.waiting_for_instruction = False

    @workflow.signal(name=SignalName.APPROVE)
    async def approve(self, _: Optional[Any] = None) -> None:
        logger.info("Received approval")
        self.event_log.append({"event": "task_approved"})
        self.task_approved = True

    @abstractmethod
    async def run(self, params: AgentTaskWorkflowParams):
        raise NotImplementedError

    async def wait_for_approval(self, task: Task, agent: Agent, content: str):
        logger.info("Waiting for instruction or approval")
        self.waiting_for_instruction = True
        if self.waiting_for_instruction and not self.task_approved:
            messages = await WorkflowHelper.execute_activity(
                activity_name=ActivityName.GET_MESSAGES_FROM_THREAD,
                request=GetMessagesFromThreadParams(
                    task_id=task.id,
                    thread_name=DEFAULT_ROOT_THREAD_NAME,
                ),
                response_type=List[Message],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
            # Find latest user message
            last_user_message = next((m for m in reversed(messages) if isinstance(m, UserMessage)), None)
            notification_message = (
                f'Agent {self.display_name} has acted and is now waiting for your input...\n\n'
                f'[Your last request]:\n{last_user_message.content}\n\n'
                f'[{self.display_name}]:\n{content}'
            )
            await WorkflowHelper.execute_activity(
                activity_name=ActivityName.SEND_NOTIFICATION,
                request=NotificationRequest(
                    topic=agent.name,
                    message=notification_message,
                    title=f'Message from [{self.display_name}]',
                    tags=["wave"],
                ),
                response_type=None,
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
        await workflow.wait_condition(lambda: not self.waiting_for_instruction or self.task_approved)
