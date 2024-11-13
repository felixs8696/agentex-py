from enum import Enum
from typing import Optional, Literal, Annotated, Union

from pydantic import Field

from agentex.utils.model_utils import BaseModel


class CreateTaskRequest(BaseModel):
    agent: str = Field(
        ...,
        title="The unique name of the agent to use to run the task",
    )
    prompt: str = Field(
        ...,
        title="The user's text prompt for the task",
    )
    require_approval: Optional[bool] = Field(
        False,
        title="Whether the task requires human approval in order to complete. "
              "If false, the task is left running until the human sends a finish",
    )


class CreateTaskResponse(BaseModel):
    id: str = Field(
        ...,
        title="Unique Task ID",
    )
    agent_id: str = Field(
        ...,
        title="The ID of the agent that is responsible for this task",
    )
    prompt: str = Field(
        ...,
        title="The user's text prompt for the task",
    )


class TaskModificationType(str, Enum):
    INSTRUCT = "instruct"
    APPROVE = "approve"
    CANCEL = "cancel"


class CancelTaskRequest(BaseModel):
    type: Literal[TaskModificationType.CANCEL] = Field(
        TaskModificationType.CANCEL,
        title="The type of instruction to send to the task",
    )


class ApproveTaskRequest(BaseModel):
    type: Literal[TaskModificationType.APPROVE] = Field(
        TaskModificationType.APPROVE,
        title="The type of instruction to send to the task",
    )


class InstructTaskRequest(BaseModel):
    type: Literal[TaskModificationType.INSTRUCT] = Field(
        TaskModificationType.INSTRUCT,
        title="The type of instruction to send to the task",
    )
    prompt: str = Field(
        ...,
        title="The user's text prompt for the task",
    )


ModifyTaskRequest = Annotated[
    Union[ApproveTaskRequest, CancelTaskRequest, InstructTaskRequest],
    Field(discriminator="type")
]
