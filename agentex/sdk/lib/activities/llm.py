from temporalio import activity

from agentex.sdk.lib.activities.names import ActivityName
from agentex.src.adapters.llm.port import LLMGateway
from agentex.src.entities.llm import LLMConfig
from agentex.src.entities.state import Completion
from agentex.utils.logging import make_logger

logger = make_logger(__name__)


class LLMActivities:

    def __init__(self, llm_gateway: LLMGateway):
        super().__init__()
        self.llm = llm_gateway

    @activity.defn(name=ActivityName.ASK_LLM)
    async def ask_llm(self, params: LLMConfig) -> Completion:
        logger.info(f"Asking LLM: {params}")
        completion = await self.llm.acompletion(**params.to_dict())
        logger.info(f"Got completion: {completion}")
        return completion
