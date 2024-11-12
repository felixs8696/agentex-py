import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.client.types.tasks import UserMessage, SystemMessage
from agentex.constants import DEFAULT_ROOT_THREAD_NAME
from agentex.sdk.execution.helpers import WorkflowHelper
from agentex.sdk.execution.workflow import AgentTaskWorkflowParams, BaseWorkflow
from agentex.sdk.lib.activities.names import ActivityName
from agentex.sdk.lib.activities.state import AppendMessagesToThreadParams
from agentex.sdk.lib.workflows.action_loop import ActionLoop
from agentex.src.entities.notifications import NotificationRequest
from agentex.utils.logging import make_logger
from constants import AGENT_NAME

logger = make_logger(__name__)


@workflow.defn(name=AGENT_NAME)
class HelloWorldWorkflow(BaseWorkflow):

    def __init__(self):
        super().__init__(display_name=AGENT_NAME)
        self.model = "gpt-4o-mini"
        self.instructions = (
            "You are an AI agent that says hello to everyone in the community"
        )

    @workflow.run
    async def run(self, params: AgentTaskWorkflowParams):
        task = params.task
        agent = params.agent

        try:
            # Give the agent the initial task
            await WorkflowHelper.execute_activity(
                activity_name=ActivityName.APPEND_MESSAGES_TO_THREAD,
                arg=AppendMessagesToThreadParams(
                    task_id=task.id,
                    thread_name=DEFAULT_ROOT_THREAD_NAME,
                    messages=[
                        SystemMessage(content=self.instructions),
                        UserMessage(content=task.prompt)
                    ],
                ),
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
            self.event_log.append({"event": "task_received", "task": task})

            # Run the tool loop
            content = None
            while True:
                self.event_log.append({"event": "tool_loop_started"})
                content = await ActionLoop.run(
                    parent_workflow=self,
                    task_id=task.id,
                    thread_name=DEFAULT_ROOT_THREAD_NAME,
                    model=self.model,
                )
                logger.info("Tool loop finished")

                if params.require_approval:
                    logger.info("Waiting for instruction or approval")
                    self.waiting_for_instruction = True
                    logger.info("Waiting for instruction or approval")
                    await workflow.wait_condition(lambda: not self.waiting_for_instruction or self.task_approved)
                    if self.task_approved:
                        logger.info("Task approved")
                        break
                    else:
                        logger.info("Task not approved, but instruction received, so continuing")
                        continue
                else:
                    break

            preface = f"🎉 {self.display_name} has completed the following task: {task.prompt}."
            await WorkflowHelper.execute_activity(
                activity_name=ActivityName.SEND_NOTIFICATION,
                arg=NotificationRequest(
                    topic=agent.name,
                    message=f"{preface}\n\n{self.display_name}:\n{content}",
                    title=self.display_name,
                    tags=["notification"],
                ),
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
            status = "completed"
            self.event_log.append({"event": "task_completed", "status": status})
        except asyncio.CancelledError as error:
            logger.warning(f"Task canceled by user: {task.id}")
            self.event_log.append({"event": "task_canceled", "error": str(error)})
            raise error

        return status
