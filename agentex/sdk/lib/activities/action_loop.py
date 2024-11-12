import json

from temporalio import activity

from agentex.sdk.lib.activities.names import ActivityName
from agentex.src.adapters.llm.port import LLMGateway
from agentex.src.entities.actions import ActionResponse, ActionRegistry
from agentex.src.entities.llm import LLMConfig, ToolMessage, SystemMessage, UserMessage
from agentex.src.entities.state import Completion
from agentex.src.services.agent_state_service import AgentStateService
from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel

logger = make_logger(__name__)


class DecideActionParams(BaseModel):
    task_id: str
    thread_name: str
    model: str


class TakeActionParams(BaseModel):
    task_id: str
    thread_name: str
    tool_call_id: str
    tool_name: str
    tool_args: str


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

        messages = await self.agent_state.threads.get_messages(task_id=task_id, thread_name=thread_name)
        completion_args = LLMConfig(
            model=model,
            messages=messages,
            tools=[action.function_call_schema() for action in self.action_class_registry.actions]
        )
        completion = await self.llm.acompletion(**completion_args.to_dict())
        message = completion.choices[0].message

        logger.info(f"Original Message: {message}")

        if not message.content and message.tool_calls:
            logger.info(f"Detected tool calls in message with no content, prompting for explanation")
            completion_args = LLMConfig(
                model=model,
                messages=[
                    *messages,
                    SystemMessage(
                        content=f"Look at all of the messages above to understand the context of the conversation. "
                                f"You have already decided to make tool calls, but you haven't provided "
                                f"an explanation for why you're making them. Please answer the user's question "
                                f"below about the tool calls you proposed.",
                    ),
                    UserMessage(
                        content=f"Give me a brief explanation for why you're making the tool calls as you are "
                                f"and how it will help the user achieve their goal. This message will be sent to the "
                                f"user as a sort of progress report on your work on the task."
                                f"These are the tool calls you decided to make:\n\n"
                                f"Tool calls:\n{message.tool_calls}\n\n"
                                f"EXAMPLE: Here are some examples of how to craft a good response. "
                                f"Please follow the same style and give the appropriate amount of detail for the user "
                                f"to feel comfortable with your progress:\n"
                                f"If the task is to send an email, and the tools available are a DraftEmail and "
                                f"SendEmail tool, when you use the DraftEmail tool, you can say:"
                                f"'In order to send an email, I need to draft the email first. Give me a moment to "
                                f"compose the email, and then I'll send it.'\n"
                                f"When you use the SendEmail tool, you can say: 'Now that I've composed the email, "
                                f"I'm sending it to the recipient. This should only take a moment.'",
                    )
                ],
            )
            explanation_completion = await self.llm.acompletion(**completion_args.to_dict())
            explanation_message = explanation_completion.choices[0].message
            completion.choices[0].message.content = explanation_message.content
            logger.info(f"Explanation provided: {explanation_message.content}")
            logger.info(f"Modified message: {completion.choices[0].message}")

        await self.agent_state.threads.append_message(
            task_id=task_id,
            thread_name=thread_name,
            message=completion.choices[0].message
        )
        return completion

    @activity.defn(name=ActivityName.TAKE_ACTION)
    async def take_action(
        self,
        params: TakeActionParams
    ) -> ActionResponse:
        task_id = params.task_id
        thread_name = params.thread_name
        tool_call_id = params.tool_call_id
        tool_name = params.tool_name
        tool_args = params.tool_args

        exception = None
        try:
            action_class = self.action_class_registry.get(tool_name)
            action_response = await action_class(**json.loads(tool_args)).execute()
        except Exception as error:
            # Log the error so the agent can fix it if possible (the activity retry loop should handle)
            action_response = ActionResponse(
                message=str(error),
                success=False,
            )
            exception = error

        tool_call_message = ToolMessage(
            content=str(action_response.message),
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

        return action_response
