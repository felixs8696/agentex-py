from abc import ABC, abstractmethod

from pydantic import BaseModel


class AgentAction(BaseModel, ABC):

    @abstractmethod
    async def execute(self) -> str:
        pass
