from typing import List, Optional, Type

from temporalio import activity

from agentex.sdk.lib.activities.names import ActivityName
from agentex.src.adapters.llm.port import LLMGateway
from agentex.src.entities.actions import Action, ActionResponse, ActionRegistry
from agentex.src.entities.llm import LLMConfig, ToolMessage
from agentex.src.entities.state import Completion
from agentex.src.services.agent_state_service import AgentStateService
from agentex.utils.model_utils import BaseModel


class DecideActionParams(BaseModel):
    task_id: str
    thread_name: str
    model: str
    actions: List[Type[Action]]


class TakeActionParams(BaseModel):
    task_id: str
    thread_name: str
    tool_call_id: str
    tool_name: str
    tool_args: dict


class ActionLoopActivities:

    def __init__(
        self,
        llm_gateway: LLMGateway,
        agent_state: AgentStateService,
        action_class_registry: ActionRegistry,
    ):
        super().__init__()
        self.llm = llm_gateway
        self.agent_state = agent_state
        self.action_class_registry = action_class_registry

    @activity.defn(name=ActivityName.DECIDE_ACTION)
    async def decide_action(
        self,
        params: DecideActionParams
    ) -> Completion:
        task_id = params.task_id
        thread_name = params.thread_name
        model = params.model
        actions = params.actions

        messages = await self.agent_state.threads.get_messages(task_id=task_id, thread_name=thread_name)
        completion_args = LLMConfig(
            model=model,
            messages=messages,
            tools=[action.function_call_schema() for action in actions]
        )
        completion = await self.llm.acompletion(**completion_args.to_dict())
        message = completion.choices[0].message
        await self.agent_state.threads.append_message(
            task_id=task_id,
            thread_name=thread_name,
            messages=message
        )
        return completion

    @activity.defn(name=ActivityName.TAKE_ACTION)
    async def take_action(
        self,
        params: TakeActionParams
    ) -> Optional[ActionResponse]:
        task_id = params.task_id
        thread_name = params.thread_name
        tool_call_id = params.tool_call_id
        tool_name = params.tool_name
        tool_args = params.tool_args

        exception = None
        try:
            action_class = self.action_class_registry.get(tool_name)
            agent_response = await action_class(**tool_args).execute()
        except Exception as error:
            # Log the error so the agent can fix it if possible (the activity retry loop should handle)
            agent_response = ActionResponse(
                message=str(error),
                success=False,
            )
            exception = error

        tool_call_message = ToolMessage(
            content=str(agent_response.message),
            tool_call_id=tool_call_id,
            name=tool_name,
        )
        await self.agent_state.threads.append_message(
            task_id=task_id,
            thread_name=thread_name,
            message=tool_call_message,
        )

        # Raise the exception, this will trigger a temporal retry
        if exception:
            raise exception

        return agent_response

