from typing import List, Dict, Any, Optional

from agentex.src.services.agent_state_repository import AgentStateRepository
from agentex.src.entities.state import AgentState
from agentex.src.entities.llm import Message


class ThreadsService:

    def __init__(self, repository: AgentStateRepository):
        self.repository = repository

    @property
    def thread_key(self):
        def _get_thread_key(task_id: str, thread_name: str) -> str:
            return f"{task_id}:{thread_name}"
        return _get_thread_key

    async def get_messages(self, task_id: str, thread_name: str) -> List[Message]:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        return state.messages

    async def get_message_by_index(self, task_id: str, thread_name: str, index: int) -> Optional[Message]:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        if 0 <= index < len(state.messages):
            return state.messages[index]
        return None

    async def batch_get_messages_by_indices(
        self, task_id: str, thread_name: str, indices: List[int]
    ) -> List[Optional[Message]]:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        return [state.messages[i] if 0 <= i < len(state.messages) else None for i in indices]

    async def append_message(self, task_id: str, thread_name: str, message: Message) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        state.messages.append(message)
        await self.repository.save(key, state)

    async def batch_append_messages(self, task_id: str, thread_name: str, messages: List[Message]) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        state.messages.extend(messages)
        await self.repository.save(key, state)

    async def override_message(self, task_id: str, thread_name: str, index: int, message: Message) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        if 0 <= index < len(state.messages):
            state.messages[index] = message
            await self.repository.save(key, state)

    async def batch_override_messages(self, task_id: str, thread_name: str, updates: Dict[int, Message]) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        for index, message in updates.items():
            if 0 <= index < len(state.messages):
                state.messages[index] = message
        await self.repository.save(key, state)

    async def insert_message(self, task_id: str, thread_name: str, index: int, message: Message) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        state.messages.insert(index, message)
        await self.repository.save(key, state)

    async def batch_insert_messages(self, task_id: str, thread_name: str, inserts: Dict[int, Message]) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        for index, message in inserts.items():
            state.messages.insert(index, message)
        await self.repository.save(key, state)

    async def delete_message(self, task_id: str, thread_name: str, index: int) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        if 0 <= index < len(state.messages):
            del state.messages[index]
            await self.repository.save(key, state)

    async def delete_all_messages(self, task_id: str, thread_name: str) -> None:
        key = self.thread_key(task_id, thread_name)
        state = await self.repository.load(key)
        state.messages = []
        await self.repository.save(key, state)

    async def delete_thread(self, task_id: str, thread_name: str) -> None:
        key = self.thread_key(task_id, thread_name)
        await self.repository.delete(key)


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

    async def set_value(self, task_id: str, key: str, value: Any) -> None:
        state = await self.repository.load(task_id)
        state.context[key] = value
        await self.repository.save(task_id, state)

    async def batch_set_value(self, task_id: str, updates: Dict[str, Any]) -> None:
        state = await self.repository.load(task_id)
        for key, value in updates.items():
            state.context[key] = value
        await self.repository.save(task_id, state)

    async def delete_value(self, task_id: str, key: str) -> None:
        state = await self.repository.load(task_id)
        if key in state.context:
            del state.context[key]
        await self.repository.save(task_id, state)

    async def batch_delete_value(self, task_id: str, keys: List[str]) -> None:
        state = await self.repository.load(task_id)
        for key in keys:
            if key in state.context:
                del state.context[key]
        await self.repository.save(task_id, state)

    async def delete_all(self, task_id: str) -> None:
        state = await self.repository.load(task_id)
        state.context = {}
        await self.repository.save(task_id, state)


class AgentStateService:
    def __init__(self, repository: AgentStateRepository):
        self.repository = repository
        self.threads = ThreadsService(repository)
        self.context = ContextService(repository)

    async def set(self, task_id: str, state: AgentState) -> None:
        await self.repository.save(task_id, state)

    async def get(self, task_id: str) -> AgentState:
        return await self.repository.load(task_id)

    async def delete(self, task_id: str) -> None:
        await self.repository.delete(task_id)
