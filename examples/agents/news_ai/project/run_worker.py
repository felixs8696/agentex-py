import asyncio

from agentex.sdk.execution.worker import AgentexWorker
from agentex.sdk.lib.activities.action_loop import ActionLoopActivities
from agentex.sdk.lib.activities.notifications import NotificationActivities
from agentex.sdk.lib.activities.state import AgentStateActivities
from agentex.src.adapters.kv_store.adapter_redis import RedisRepository
from agentex.src.adapters.llm.adapter_litellm import LiteLLMGateway
from agentex.src.adapters.notifications.adapter_ntfy import NtfyGateway
from agentex.src.entities.actions import ActionRegistry
from agentex.src.services.agent_state_repository import AgentStateRepository
from agentex.src.services.agent_state_service import AgentStateService
from examples.agents.news_ai.project.activities import FetchNews, ProcessNews, WriteSummary, ReportTerminalFailure
from examples.agents.news_ai.project.constants import TASK_QUEUE_NAME, BASE_ACTION_REGISTRY_KEY
from workflow import NewsAIWorkflow


async def main():
    worker = AgentexWorker(task_queue=TASK_QUEUE_NAME)

    # Initialize adapters
    redis_repository = RedisRepository()
    llm_gateway = LiteLLMGateway()
    notification_gateway = NtfyGateway()

    # Initialize services
    agent_state_repository = AgentStateRepository(kv_store=redis_repository)
    agent_state_service = AgentStateService(repository=agent_state_repository)

    # Register actions
    action_registry = ActionRegistry(actions={
        BASE_ACTION_REGISTRY_KEY: [
            FetchNews,
            ProcessNews,
            WriteSummary,
            ReportTerminalFailure,
        ]
    })

    agent_state_activities = AgentStateActivities(
        agent_state=agent_state_service,
    )
    action_loop_activities = ActionLoopActivities(
        llm_gateway=llm_gateway,
        agent_state=agent_state_service,
        action_class_registry=action_registry,
    )
    notification_activities = NotificationActivities(
        notification_gateway=notification_gateway,
    )

    await worker.run(
        activities=[
            agent_state_activities.append_messages_to_thread,
            agent_state_activities.get_messages_from_thread,
            action_loop_activities.decide_action,
            action_loop_activities.take_action,
            notification_activities.send_notification,
        ],
        workflow=NewsAIWorkflow,
    )


if __name__ == "__main__":
    asyncio.run(main())
