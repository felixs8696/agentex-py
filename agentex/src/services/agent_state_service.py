from typing import List, Dict, Any, Optional

from agentex.exceptions import ClientError
from agentex.src.entities.actions import Artifact
from agentex.src.entities.llm import Message
from agentex.src.entities.state import Thread, ContextKey
from agentex.src.services.agent_state_repository import AgentStateRepository


class ThreadsService:

    def __init__(self, repository: AgentStateRepository):
        self.repository = repository

    async def get_messages(self, task_id: str, thread_name: str) -> List[Message]:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        return state.threads[thread_name].messages

    async def get_message_by_index(self, task_id: str, thread_name: str, index: int) -> Optional[Message]:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        if 0 <= index < len(state.threads[thread_name].messages):
            return state.threads[thread_name].messages[index]
        return None

    async def batch_get_messages_by_indices(
        self, task_id: str, thread_name: str, indices: List[int]
    ) -> List[Optional[Message]]:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        return [
            state.threads[thread_name].messages[i]
            if 0 <= i < len(state.threads[thread_name].messages)
            else None
            for i in indices
        ]

    async def append_message(self, task_id: str, thread_name: str, message: Message) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        state.threads[thread_name].messages.append(message)
        await self.repository.save(task_id, state)

    async def batch_append_messages(self, task_id: str, thread_name: str, messages: List[Message]) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        state.threads[thread_name].messages.extend(messages)
        await self.repository.save(task_id, state)

    async def override_message(self, task_id: str, thread_name: str, index: int, message: Message) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        if 0 <= index < len(state.threads[thread_name].messages):
            state.threads[thread_name].messages[index] = message
            await self.repository.save(task_id, state)

    async def batch_override_messages(self, task_id: str, thread_name: str, updates: Dict[int, Message]) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        for index, message in updates.items():
            if 0 <= index < len(state.threads[thread_name].messages):
                state.threads[thread_name].messages[index] = message
        await self.repository.save(task_id, state)

    async def insert_message(self, task_id: str, thread_name: str, index: int, message: Message) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        state.threads[thread_name].messages.insert(index, message)
        await self.repository.save(task_id, state)

    async def batch_insert_messages(self, task_id: str, thread_name: str, inserts: Dict[int, Message]) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        for index, message in inserts.items():
            state.threads[thread_name].messages.insert(index, message)
        await self.repository.save(task_id, state)

    async def delete_message(self, task_id: str, thread_name: str, index: int) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        if 0 <= index < len(state.threads[thread_name].messages):
            del state.threads[thread_name].messages[index]
            await self.repository.save(task_id, state)

    async def delete_all_messages(self, task_id: str, thread_name: str) -> None:
        state = await self.repository.load(task_id)
        if thread_name not in state.threads:
            state.threads[thread_name] = Thread()
        state.threads[thread_name].messages = []
        await self.repository.save(task_id, state)

    async def delete_thread(self, task_id: str, thread_name: str) -> None:
        state = await self.repository.load(task_id)
        if thread_name in state.threads:
            del state.threads[thread_name]
            await self.repository.save(task_id, state)


class ContextService:
    def __init__(self, repository: AgentStateRepository):
        self.repository = repository

    async def get_all(self, task_id: str) -> Dict[str, Any]:
        state = await self.repository.load(task_id)
        return state.context

    async def get_value(self, task_id: str, key: str) -> Optional[Any]:
        state = await self.repository.load(task_id)
        return state.context.get(key)

    async def batch_get_values(self, task_id: str, keys: List[str]) -> Dict[str, Optional[Any]]:
        state = await self.repository.load(task_id)
        return {key: state.context.get(key) for key in keys}

    async def get_artifact(self, task_id: str, artifact_name: str) -> Optional[Artifact]:
        state = await self.repository.load(task_id)
        if ContextKey.ARTIFACTS not in state.context:
            state.context[ContextKey.ARTIFACTS] = {}
        artifact_dict = state.context[ContextKey.ARTIFACTS].get(artifact_name)
        if artifact_dict:
            return Artifact.from_dict(artifact_dict)
        return None

    async def get_artifacts(self, task_id: str) -> Dict[str, Artifact]:
        state = await self.repository.load(task_id)
        if ContextKey.ARTIFACTS not in state.context:
            state.context[ContextKey.ARTIFACTS] = {}
        return {name: Artifact.from_dict(artifact) for name, artifact in state.context[ContextKey.ARTIFACTS].items()}

    async def set_value(self, task_id: str, key: str, value: Any) -> None:
        state = await self.repository.load(task_id)
        state.context[key] = value
        await self.repository.save(task_id, state)

    async def set_artifact(
        self, task_id: str, artifact_name: str, artifact: Artifact, overwrite: bool = False
    ) -> None:
        state = await self.repository.load(task_id)
        if ContextKey.ARTIFACTS not in state.context:
            state.context[ContextKey.ARTIFACTS] = {}
        if overwrite or artifact_name not in state.context[ContextKey.ARTIFACTS]:
            state.context[ContextKey.ARTIFACTS][artifact_name] = artifact
            await self.repository.save(task_id, state)
        else:
            raise ClientError(f"Artifact with name '{artifact_name}' already exists in the context.")

    async def batch_set_value(self, task_id: str, updates: Dict[str, Any]) -> None:
        state = await self.repository.load(task_id)
        for key, value in updates.items():
            state.context[key] = value
        await self.repository.save(task_id, state)

    async def batch_set_artifacts(self, task_id: str, artifacts: List[Artifact], overwrite: bool = False) -> None:
        state = await self.repository.load(task_id)
        if ContextKey.ARTIFACTS not in state.context:
            state.context[ContextKey.ARTIFACTS] = {}
        for artifact in artifacts:
            if overwrite or artifact.name not in state.context[ContextKey.ARTIFACTS]:
                state.context[ContextKey.ARTIFACTS][artifact.name] = artifact
            else:
                raise ClientError(f"Artifact with name '{artifact.name}' already exists in the context.")
        await self.repository.save(task_id, state)

    async def delete_value(self, task_id: str, key: str) -> None:
        state = await self.repository.load(task_id)
        if key in state.context:
            del state.context[key]
        await self.repository.save(task_id, state)

    async def delete_artifact(self, task_id: str, artifact_name: str) -> None:
        state = await self.repository.load(task_id)
        if ContextKey.ARTIFACTS in state.context and artifact_name in state.context[ContextKey.ARTIFACTS]:
            del state.context[ContextKey.ARTIFACTS][artifact_name]
            await self.repository.save(task_id, state)

    async def batch_delete_value(self, task_id: str, keys: List[str]) -> None:
        state = await self.repository.load(task_id)
        for key in keys:
            if key in state.context:
                del state.context[key]
        await self.repository.save(task_id, state)

    async def batch_delete_artifacts(self, task_id: str, artifact_names: List[str]) -> None:
        state = await self.repository.load(task_id)
        if ContextKey.ARTIFACTS in state.context:
            for artifact_name in artifact_names:
                if artifact_name in state.context[ContextKey.ARTIFACTS]:
                    del state.context[ContextKey.ARTIFACTS][artifact_name]
        await self.repository.save(task_id, state)

    async def delete_all(self, task_id: str) -> None:
        state = await self.repository.load(task_id)
        state.context = {}
        await self.repository.save(task_id, state)


class AgentStateService:
    def __init__(self, repository: AgentStateRepository):
        self.threads = ThreadsService(repository)
        self.context = ContextService(repository)
