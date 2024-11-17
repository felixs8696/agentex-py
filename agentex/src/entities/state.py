from collections import defaultdict
from enum import Enum
from typing import List, Dict, Any, Optional, Literal

from pydantic import Field

from agentex.src.entities.llm import AssistantMessage, Message
from agentex.utils.model_utils import BaseModel


class Choice(BaseModel):
    finish_reason: Literal["stop", "length", "content_filter", "tool_calls"]
    index: int
    message: AssistantMessage


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Completion(BaseModel):
    choices: List[Choice]
    created: Optional[int] = None
    model: Optional[str] = None
    usage: Usage


class Thread(BaseModel):
    messages: List[Message] = Field(
        default_factory=list,
    )


class AgentState(BaseModel):
    """State object that holds the agent's transaction history and context."""
    threads: Optional[Dict[str, Thread]] = Field(
        default_factory=lambda: defaultdict(Thread),
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
    )


class ContextKey(str, Enum):
    ARTIFACTS = "artifacts"
