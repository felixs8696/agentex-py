import asyncio

from agentex.sdk.execution.worker import AgentexWorker
from agentex.sdk.lib.activities.action_loop import ActionLoopActivities
from agentex.sdk.lib.activities.llm import LLMActivities
from agentex.sdk.lib.activities.notifications import NotificationActivities
from agentex.sdk.lib.activities.state import AgentStateActivities
from agentex.src.adapters.kv_store.adapter_redis import RedisRepository
from agentex.src.adapters.llm.adapter_litellm import LiteLLMGateway
from agentex.src.adapters.notifications.adapter_ntfy import NtfyGateway
from agentex.src.services.agent_state_repository import AgentStateRepository
from agentex.src.services.agent_state_service import AgentStateService
from constants import TASK_QUEUE_NAME, ActionRegistryKey
from critic_actions import CriticActions
from workflow import DocWriterActorCriticWorkflow
from writer_actions import WriterActions


async def main():
    worker = AgentexWorker(task_queue=TASK_QUEUE_NAME)

    # Initialize adapters
    redis_repository = RedisRepository()
    llm_gateway = LiteLLMGateway()
    notification_gateway = NtfyGateway()

    # Initialize services
    agent_state_repository = AgentStateRepository(kv_store=redis_repository)
    agent_state_service = AgentStateService(repository=agent_state_repository)

    writer_actions = WriterActions(agent_state_service=agent_state_service)
    critic_actions = CriticActions(agent_state_service=agent_state_service)

    agent_state_activities = AgentStateActivities(
        agent_state=agent_state_service,
    )
    action_loop_activities = ActionLoopActivities(
        llm_gateway=llm_gateway,
        agent_state=agent_state_service,
        action_registries={
            ActionRegistryKey.WRITER: writer_actions,
            ActionRegistryKey.CRITIC: critic_actions,
        },
    )
    notification_activities = NotificationActivities(
        notification_gateway=notification_gateway,
    )
    llm_activities = LLMActivities(
        llm_gateway=llm_gateway,
    )

    await worker.run(
        activities=[
            agent_state_activities.append_messages_to_thread,
            agent_state_activities.get_messages_from_thread,
            agent_state_activities.add_artifact_to_context,
            action_loop_activities.decide_action,
            action_loop_activities.take_action,
            llm_activities.ask_llm,
            notification_activities.send_notification,
        ],
        workflow=DocWriterActorCriticWorkflow,
    )


if __name__ == "__main__":
    asyncio.run(main())