from pydantic import Field

from agentex.src.entities.actions import Action, ActionResponse


class HelloAdam(Action):
    """
    Say hello to Adam.
    """

    name: str = Field(
        ...,
        description="The name of the person for Adam to say hello back to."
    )

    async def execute(self) -> ActionResponse:
        return ActionResponse(
            message=f"Adam: Hello, {self.name}!",
        )


class HelloJessica(Action):
    """
    Say hello to Jessica.
    """

    name: str = Field(
        ...,
        description="The name of the person for Jessica to say hello back to."
    )

    async def execute(self) -> ActionResponse:
        return ActionResponse(
            message=f"Jessica: Hello, {self.name}!",
        )
