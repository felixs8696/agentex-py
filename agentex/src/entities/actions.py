from typing import List, Any, Dict, Optional
from typing import Union, Literal

from pydantic import Field

from agentex.utils.model_utils import BaseModel


class FunctionSchema(BaseModel):
    name: str
    description: Optional[str]
    parameters: Any


class FunctionCallSchema(BaseModel):
    type: Literal["function"] = Field("function")
    function: FunctionSchema


class Artifact(BaseModel):
    name: str = Field(
        ...,
        description="The name of the artifact."
    )
    description: Optional[str] = Field(
        None,
        description="The description of the artifact."
    )
    content: Union[Dict, List, str, int, float, bool] = Field(
        ...,
        description="The content of the artifact."
    )


class ActionResponse(BaseModel):
    """
    A response that represents a   message response to the agent and something you want to add to the agent's context.
    This will be added to the agent's state.messages as a tool message and to the agent's state.context.
    """
    message: Union[Dict, List, str, int, float, bool] = Field(
        ...,
        description="The message content used to respond to the agent about the action results. If you want to store "
                    "a larger payload that the agent doesn't need persistent access to, use the context field."
    )
    artifacts: Optional[List[Artifact]] = Field(
        None,
        description="If a larger payload is needed to be stored in the agent's context, use this field. This will not "
                    "be persistently stored in the agent's context, but the agent knows how to retrieve this "
                    "information when it needs it. It will be exposed to the user on the UI as an artifact."
    )
    success: bool = Field(
        True,
        description="Whether the action was successful or not."
    )
