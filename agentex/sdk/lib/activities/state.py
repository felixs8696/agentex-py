from enum import Enum
from typing import List

from temporalio import activity

from agentex.sdk.lib.activities.names import ActivityName
from agentex.src.entities.actions import Artifact
from agentex.src.entities.llm import Message
from agentex.src.services.agent_state_service import AgentStateService
from agentex.utils.model_utils import BaseModel


class ContextKey(str, Enum):
    ARTIFACTS = "artifacts"


class AppendMessagesToThreadParams(BaseModel):
    task_id: str
    thread_name: str
    messages: List[Message]


class GetMessagesFromThreadParams(BaseModel):
    task_id: str
    thread_name: str


class AddArtifactToContextParams(BaseModel):
    task_id: str
    artifact: Artifact


class AgentStateActivities:

    def __init__(self, agent_state: AgentStateService):
        super().__init__()
        self.agent_state = agent_state

    @activity.defn(name=ActivityName.APPEND_MESSAGES_TO_THREAD)
    async def append_messages_to_thread(self, params: AppendMessagesToThreadParams) -> List[Message]:
        task_id = params.task_id
        thread_name = params.thread_name
        messages = params.messages

        await self.agent_state.threads.batch_append_messages(
            task_id=task_id,
            thread_name=thread_name,
            messages=messages
        )
        messages = await self.agent_state.threads.get_messages(
            task_id=task_id,
            thread_name=thread_name
        )
        return messages

    @activity.defn(name=ActivityName.GET_MESSAGES_FROM_THREAD)
    async def get_messages_from_thread(self, params: GetMessagesFromThreadParams) -> List[Message]:
        task_id = params.task_id
        thread_name = params.thread_name

        messages = await self.agent_state.threads.get_messages(
            task_id=task_id,
            thread_name=thread_name
        )
        return messages

    @activity.defn(name=ActivityName.ADD_ARTIFACT_TO_CONTEXT)
    async def add_artifact_to_context(self, params: AddArtifactToContextParams) -> None:
        task_id = params.task_id
        artifact = params.artifact

        artifacts = await self.agent_state.context.get_value(
            task_id=task_id,
            key=ContextKey.ARTIFACTS,
        )
        if artifacts is None:
            artifacts = []
        artifacts.append(artifact.to_dict())
        await self.agent_state.context.set_value(
            task_id=task_id,
            key=ContextKey.ARTIFACTS,
            value=artifacts
        )
