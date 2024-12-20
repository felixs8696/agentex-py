from typing import List, Optional, Union, Type, Any
from typing import Literal, Annotated

from pydantic import Field

from agentex.utils.model_utils import BaseModel


class LLMConfig(BaseModel):
    model: str
    messages: List = []
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    stream: Optional[bool] = None
    stream_options: Optional[dict] = None
    stop: Optional[Union[str, list]] = None
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[dict] = None
    response_format: Optional[Union[dict, Type[BaseModel]]] = None
    seed: Optional[int] = None
    tools: Optional[List] = None
    tool_choice: Optional[str] = None
    parallel_tool_calls: Optional[bool] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = None


class ContentPartText(BaseModel):
    text: str = Field(
        ...,
        description="The text content."
    )
    type: Literal["text"] = Field(
        ...,
        description="The type of the content part."
    )


class ImageURL(BaseModel):
    url: str = Field(
        ...,
        description="Either a URL of the image or the base64 encoded image data."
    )
    detail: Literal["auto", "low", "high"] = Field(
        ...,
        description="""Specifies the detail level of the image.

Learn more in the
[Vision guide](https://platform.openai.com/docs/guides/vision/low-or-high-fidelity-image-understanding).
"""
    )


class ContentPartImage(BaseModel):
    image_url: ImageURL = Field(
        ...,
        description="The image URL."
    )
    type: Literal["image_url"] = Field(
        ...,
        description="The type of the content part."
    )


ContentPart = Union[ContentPartText, ContentPartImage]


class SystemMessage(BaseModel):
    role: Literal["system"] = Field(
        "system",
        description="The role of the messages author, in this case `system`."
    )
    content: str = Field(
        ...,
        description="The contents of the system message."
    )


class UserMessage(BaseModel):
    role: Literal["user"] = Field(
        "user",
        description="The role of the messages author, in this case `user`."
    )
    content: str = Field(
        ...,
        description="The contents of the user message."
    )


class ToolCall(BaseModel):
    name: str = Field(
        ...,
        description="The name of the function to call."
    )
    arguments: str = Field(
        ...,
        description="""
The arguments to call the function with, as generated by the model in JSON
format. Note that the model does not always generate valid JSON, and may
hallucinate parameters not defined by your function schema. Validate the
arguments in your code before calling your function.
"""
    )


class ToolCallRequest(BaseModel):
    type: Literal["function"] = Field(
        "function",
        description="The type of the tool. Currently, only `function` is supported."
    )
    id: str = Field(
        ...,
        description="The ID of the tool call request."
    )
    function: ToolCall = Field(
        ...,
        description="The function that the model is requesting."
    )


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = Field(
        "assistant",
        description="The role of the messages author, in this case `assistant`."
    )
    content: Optional[str] = Field(
        None,
        description="""The contents of the assistant message.

Required unless `tool_calls` or `function_call` is specified.
"""
    )
    tool_calls: Optional[List[ToolCallRequest]] = Field(
        default_factory=list,
        description="The tool calls generated by the model, such as function calls."
    )
    parsed: Optional[Any] = Field(
        None,
        description="The parsed content of the message to a specific type"
    )


class ToolMessage(BaseModel):
    role: Literal["tool"] = Field(
        "tool",
        description="The role of the messages author, in this case `tool`."
    )
    content: Union[str, List[ContentPart]] = Field(
        ...,
        description="The contents of the tool message."
    )
    tool_call_id: str = Field(
        ...,
        description="Tool call that this message is responding to."
    )
    name: str = Field(
        ...,
        description="The name of the tool called."
    )


Message = Annotated[
    Union[
        SystemMessage,
        UserMessage,
        AssistantMessage,
        ToolMessage
    ],
    Field(
        discriminator="role"
    )
]
