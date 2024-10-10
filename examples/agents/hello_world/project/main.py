from pydantic import Field

from agentex.sdk.agent import Agent
from agentex.sdk.actions import AgentAction

agent = Agent(
    name="HelloWorld",
    description="An AI agent application that says hi to everyone in your community",
    model="gpt-4o",
    version="0.0.0",
    instructions="You are an AI agent application whose purpose is to say hi to everyone in your community",
)


@agent.action
class HelloAdam(AgentAction):
    """
    Say hello to Adam
    """
    agent_name: str = Field(..., description="Your own name, so that Adam can say hello back to you.")

    async def execute(self) -> str:
        print("Hello Adam!")
        return f"Adam: 'Hello {self.agent_name}!'"


@agent.action
class HelloJessica(AgentAction):
    """
    Say hello to Jessica
    """
    agent_name: str = Field(..., description="Your own name, so that Jessica can say hello back to you.")

    async def execute(self) -> str:
        print("Hello Jessica!")
        return f"Jessica: 'Hello {self.agent_name}!'"
