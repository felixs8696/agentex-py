from abc import ABC, abstractmethod
from typing import Any, Dict, List


class KeyValueRepository(ABC):

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def batch_set(self, updates: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def batch_get(self, keys: List[str]) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def batch_delete(self, keys: List[str]) -> List[Any]:
        raise NotImplementedError
