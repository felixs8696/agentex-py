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
from examples.agents.temporal_news_ai.project.activities import FetchNews, ProcessNews, WriteSummary

logger = make_logger(__name__)


@workflow.defn
class NewsAIWorkflow(BaseWorkflow):

    def __init__(self):
        super().__init__(
            name="NewsAI",
            description=(
                "An AI agent that dynamically discovers and tracks the hottest AI tech companies and news without "
                "hard-coding."
            ),
            model="gpt-4o-mini",
            version="0.0.0",
            instructions=(
                "You are an AI agent designed to fetch and summarize the latest AI technology news. "
                "Your tasks include fetching news articles, processing provided company data, "
                "and compiling a summarized document suitable for a CEO of a budding startup."
            ),
        )

    @workflow.run
    async def run(self, params: AgentTaskWorkflowParams):
        task = params.task

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
                    actions=[FetchNews, ProcessNews, WriteSummary],
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

            preface = f"🎉 {self.name} has completed the following task: {task.prompt}."
            await WorkflowHelper.execute_activity(
                activity_name=ActivityName.SEND_NOTIFICATION,
                arg=NotificationRequest(
                    topic=task.id,
                    message=f"{preface}\n\n{self.name}:\n{content}",
                    title=self.name,
                    tags=["notification"],
                    priority=3,
                    actions=[
                        {
                            "action": "approve",
                            "label": "Approve",
                            "url": "https://example.com/approve",
                            "clear": True
                        },
                        {
                            "action": "reject",
                            "label": "Reject",
                            "url": "https://example.com/reject",
                            "clear": True
                        }
                    ]
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
