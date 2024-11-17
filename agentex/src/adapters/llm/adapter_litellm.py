import litellm as llm

from agentex.src.adapters.llm.port import LLMGateway
from agentex.src.entities.state import Completion
from agentex.utils.logging import make_logger

logger = make_logger(__name__)


class LiteLLMGateway(LLMGateway):

    def completion(self, *args, **kwargs) -> Completion:
        response = llm.completion(*args, **kwargs)
        choice = response.choices[0]
        try:
            logger.info(f"Completion response: {response}")
            return Completion.from_orm(response)
        except Exception as e:
            raise Exception(f"Error parsing response: {e}, Choice: {choice}")

    async def acompletion(self, *args, **kwargs) -> Completion:
        response = await llm.acompletion(*args, **kwargs)
        choice = response.choices[0]
        try:
            logger.info(f"Completion response: {response}")
            return Completion.from_orm(response)
        except Exception as e:
            raise Exception(f"Error parsing response: {e}, Choice: {choice}")
