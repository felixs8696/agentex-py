import asyncio

from agentex.sdk.execution.worker import AgentexWorker
from agentex.sdk.lib.activities.action_loop import ActionLoopActivities
from agentex.sdk.lib.activities.state import AgentStateActivities
from agentex.src.adapters.kv_store.adapter_redis import RedisRepository
from agentex.src.adapters.llm.adapter_litellm import LiteLLMGateway
from agentex.src.entities.actions import ActionRegistry
from agentex.src.services.agent_state_repository import AgentStateRepository
from agentex.src.services.agent_state_service import AgentStateService
from workflow import NewsAIWorkflow, FetchNews, ProcessNews, WriteSummary

TASK_QUEUE_NAME = "news_ai_task_queue"


async def main():
    worker = AgentexWorker(
        task_queue=TASK_QUEUE_NAME,
    )

    # Initialize adapters
    redis_repository = RedisRepository()
    llm_gateway = LiteLLMGateway()

    # Initialize services
    agent_state_repository = AgentStateRepository(kv_store=redis_repository)
    agent_state_service = AgentStateService(repository=agent_state_repository)

    # Register actions
    action_registry = ActionRegistry(actions=[
        FetchNews,
        ProcessNews,
        WriteSummary,
    ])

    agent_state_activities = AgentStateActivities(
        agent_state=agent_state_service,
    )
    action_loop_activities = ActionLoopActivities(
        llm_gateway=llm_gateway,
        agent_state=agent_state_service,
        action_class_registry=action_registry,
    )

    await worker.run(
        activities=[
            agent_state_activities.append_messages_to_thread,
            action_loop_activities.decide_action,
            action_loop_activities.take_action,
        ],
        workflow=NewsAIWorkflow,
    )


if __name__ == "__main__":
    asyncio.run(main())
