import asyncio
from datetime import timedelta
from typing import List, Type

from temporalio.common import RetryPolicy

from agentex.client.types.tasks import Completion
from agentex.sdk.execution.helpers import WorkflowHelper
from agentex.sdk.execution.workflow import BaseWorkflow
from agentex.sdk.lib.activities.action_loop import DecideActionParams, TakeActionParams
from agentex.sdk.lib.activities.names import ActivityName
from agentex.src.entities.actions import Action
from agentex.utils.logging import make_logger

logger = make_logger(__name__)


class ActionLoop:

    @staticmethod
    async def run(
        parent_workflow: BaseWorkflow, task_id: str, thread_name: str, model: str, actions: List[Type[Action]]
    ) -> str:
        content = None
        finish_reason = None
        while finish_reason not in ("stop", "length", "content_filter"):
            # Execute decision activity
            completion = await WorkflowHelper.execute_activity(
                activity_name=ActivityName.DECIDE_ACTION,
                arg=DecideActionParams(
                    task_id=task_id,
                    thread_name=thread_name,
                    model=model,
                    actions=actions,
                ),
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=5),
                response_model=Completion,
            )
            parent_workflow.event_log.append({"event": "decision_made", "completion": completion.dict()})
            finish_reason = completion.finish_reason
            decision = completion.message
            tool_calls = decision.tool_calls
            content = decision.content

            # Execute tool activities if requested
            take_action_activities = []
            if decision.tool_calls:
                logger.info(f"Executing tool calls: {tool_calls}")
                parent_workflow.event_log.append({"event": "executing_tool_calls"})
                for tool_call in tool_calls:
                    take_action_activity = asyncio.create_task(
                        WorkflowHelper.execute_activity(
                            activity_name=ActivityName.TAKE_ACTION,
                            arg=TakeActionParams(
                                tool_call_id=tool_call.id,
                                tool_name=tool_call.name,
                                tool_args=tool_call.args,
                            ),
                            start_to_close_timeout=timedelta(seconds=60),
                            retry_policy=RetryPolicy(maximum_attempts=5),
                        )
                    )
                    parent_workflow.event_log.append({"event": "executing_tool_call", "tool_call": tool_call.dict()})
                    take_action_activities.append(take_action_activity)

            # Wait for all tool activities to complete
            await asyncio.gather(*take_action_activities)

        return content
