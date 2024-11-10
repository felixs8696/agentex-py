from typing import Any, List, Dict

from agentex.src.adapters.kv_store.port import KeyValueRepository


class LocalKeyValueRepository(KeyValueRepository):
    def __init__(self):
        self.store = {}

    async def set(self, key: str, value: Any) -> None:
        self.store[key] = value

    async def batch_set(self, updates: Dict[str, Any]) -> None:
        self.store.update(updates)

    async def get(self, key: str) -> Any:
        return self.store.get(key)

    async def batch_get(self, keys: List[str]) -> List[Any]:
        return [self.store.get(key) for key in keys]

    async def delete(self, key: str) -> Any:
        return self.store.pop(key, None)

    async def batch_delete(self, keys: List[str]) -> List[Any]:
        return [self.store.pop(key, None) for key in keys]
