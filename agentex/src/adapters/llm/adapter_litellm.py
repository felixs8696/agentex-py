import litellm as llm

from agentex.src.adapters.llm.port import LLMGateway
from agentex.src.entities.state import Completion


class LiteLLMGateway(LLMGateway):

    def completion(self, *args, **kwargs) -> Completion:
        response = llm.completion(*args, **kwargs)
        choice = response.choices[0]
        if kwargs.get('response_format'):
            response.choices[0].message.parsed = kwargs['response_format'].from_json(choice.message.content)
        try:
            return Completion.from_orm(response)
        except Exception as e:
            raise Exception(f"Error parsing response: {e}, Choice: {choice}")

    async def acompletion(self, *args, **kwargs) -> Completion:
        response = await llm.acompletion(*args, **kwargs)
        choice = response.choices[0]
        if kwargs.get('response_format'):
            response.choices[0].message.parsed = kwargs['response_format'].from_json(choice.message.content)
        try:
            return Completion.from_orm(response)
        except Exception as e:
            raise Exception(f"Error parsing response: {e}, Choice: {choice}")
