import os
from typing import Any, List, Dict

import redis.asyncio as redis

from agentex.src.adapters.kv_store.port import KeyValueRepository


class RedisRepository(KeyValueRepository):
    def __init__(self):
        self.redis = redis.from_url(os.environ.get("REDIS_URL"))

    async def set(self, key: str, value: Any) -> None:
        return await self.redis.set(key, value)

    async def batch_set(self, updates: Dict[str, Any]) -> None:
        return await self.redis.mset(updates)

    async def get(self, key: str) -> Any:
        return await self.redis.get(key)

    async def batch_get(self, keys: List[str]) -> List[Any]:
        return await self.redis.mget(keys)

    async def delete(self, key: str) -> Any:
        return await self.redis.delete(key)

    async def batch_delete(self, keys: List[str]) -> List[Any]:
        return await self.redis.delete(*keys)
