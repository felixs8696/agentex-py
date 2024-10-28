from pydantic import Field

from agentex.sdk.actions import AgentAction, AgentResponse, Artifact
from agentex.sdk.agent import Agent

agent = Agent(
    name="DocWriter",
    description="An AI agent that helps me write documents.",
    model="gpt-4o",
    version="0.0.0",
    instructions="You are an AI agent whose purpose is to help the user write documents. "
                 "You should try to do as much as you can on your own using the tools available, but also ask the "
                 "user for assistance when you need clarification, someone to check your work, or any other help.",
)


@agent.action(test_payload={"name": "test", "description": "test", "markdown_content": "test"})
class WriteDocument(AgentAction):
    """
    Write a document with the given content.
    """
    name: str = Field(
        ...,
        description="The name of the document to write. Use the name of an existing document to overwrite it."
    )
    description: str = Field(
        None,
        description="A short, comprehensive description of the contents of this document. Needs to be detailed "
                    "enough for the AI to understand when to use this document."
    )
    markdown_content: str = Field(..., description="The content of the document to write written in markdown.")

    async def execute(self) -> AgentResponse:
        return AgentResponse(
            message=f"Document '{self.name}' written successfully.",
            artifacts=[
                Artifact(
                    name=self.name,
                    description=self.description,
                    content=self.markdown_content
                )
            ]
        )
