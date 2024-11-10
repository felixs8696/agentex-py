import litellm as llm

from agentex.src.adapters.llm.port import LLMGateway
from agentex.src.entities.state import Completion


class LiteLLMGateway(LLMGateway):

    def completion(self, *args, **kwargs) -> Completion:
        choice = llm.completion(*args, **kwargs).choices[0]
        if kwargs.get('response_format'):
            choice.message.parsed = kwargs['response_format'].from_json(choice.message.content)
        return Completion.from_orm(choice)

    async def acompletion(self, *args, **kwargs) -> Completion:
        response = await llm.acompletion(*args, **kwargs)
        choice = response.choices[0]
        if kwargs.get('response_format'):
            choice.message.parsed = kwargs['response_format'].from_json(choice.message.content)
        try:
            return Completion.from_orm(choice)
        except Exception as e:
            raise Exception(f"Error parsing response: {e}, Choice: {choice}")
