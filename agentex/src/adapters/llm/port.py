from abc import ABC, abstractmethod

from agentex.src.entities.llm import Message


class LLMGateway(ABC):

    @abstractmethod
    def completion(self, *args, **kwargs) -> Message:
        raise NotImplementedError

    @abstractmethod
    async def acompletion(self, *args, **kwargs) -> Message:
        raise NotImplementedError
