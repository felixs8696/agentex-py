import asyncio
from datetime import timedelta
from typing import List

from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.constants import DEFAULT_ROOT_THREAD_NAME
from agentex.sdk.execution.helpers import WorkflowHelper
from agentex.sdk.execution.workflow import AgentTaskWorkflowParams, BaseWorkflow
from agentex.sdk.lib.activities.names import ActivityName
from agentex.sdk.lib.activities.state import AppendMessagesToThreadParams, AddArtifactToContextParams
from agentex.sdk.lib.workflows.action_loop import ActionLoop
from agentex.src.entities.actions import Artifact
from agentex.src.entities.llm import Message, UserMessage, SystemMessage, LLMConfig, AssistantMessage
from agentex.src.entities.notifications import NotificationRequest
from agentex.src.entities.state import Completion
from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel
from constants import AGENT_NAME, ActionRegistryKey

logger = make_logger(__name__)


class CriticSatisfaction(BaseModel):
    satisfied: bool


@workflow.defn(name=AGENT_NAME)
class DocWriterActorCriticWorkflow(BaseWorkflow):

    def __init__(self):
        super().__init__(display_name=AGENT_NAME)
        self.model = "gpt-4o"
        self.writer_instructions = (
            "You are an AI agent designed to write a document based on the prompt provided by the user. "
            "You are also being evaluated by a critic and should address all criticisms given to you. Once "
            "you finish iterating, always save any artifacts you produce so others can read them."
        )
        self.critic_instructions = (
            "You are an AI agent designed to provide feedback on the document written by the writer agent. Consider "
            "all nuance of what the user is asking and be very critical of the document written by the writer. "
            "Be especially careful of any audience personas that the user says they are sending the document to "
            "to consider their point of views as well. You should only be satisfied when all of your criticisms are "
            "addressed."
        )

    @workflow.run
    async def run(self, params: AgentTaskWorkflowParams):
        task = params.task
        agent = params.agent

        writer_thread_name = "writer"
        final_responses_thread_name = "final_responses"

        try:
            self.event_log.append({"event": "task_received", "task": task})

            # Give the writer agent the initial instructions
            await self._add_messages_to_thread(
                task_id=task.id,
                thread_name=writer_thread_name,
                messages=[
                    SystemMessage(content=self.writer_instructions),
                    UserMessage(content=task.prompt)
                ],
            )

            # Run the tool loop
            content = None
            while True:
                self.event_log.append({"event": "tool_loop_started"})
                critic_satisfied = False
                iteration = 0
                critic_response = None
                while not critic_satisfied:
                    if critic_response:
                        # Give the writer agent the initial instructions
                        await self._add_messages_to_thread(
                            task_id=task.id,
                            thread_name=writer_thread_name,
                            messages=[
                                UserMessage(
                                    content=f"Remember:\n"
                                            f"These are your instructions: {self.writer_instructions}"
                                            f"your original ask from the user was the following:\n"
                                            f"{task.prompt}"
                                            f"However, the critic agent was not satisfied with the document you wrote."
                                            f"Here is the feedback from the critic agent:\n"
                                            f"{critic_response}"
                                ),
                            ],
                        )

                    # Allow the writer agent to attempt to (re)write the document
                    # and reason with itself using the latest critic feedback
                    latest_content = await ActionLoop.run(
                        parent_workflow=self,
                        task_id=task.id,
                        thread_name=writer_thread_name,
                        action_registry_key=ActionRegistryKey.WRITER,
                        model=self.model,
                    )
                    # await self._save_artifact(task_id=task.id, artifact=Artifact(
                    #     name=f"writer_draft_{iteration + 1}",
                    #     content=latest_content,
                    # ))

                    logger.info("Writer tool loop finished")

                    # Give the critic agent the instructions and the latest content
                    # Always keep the critic message history clean and unpolluted
                    critic_thread_name = f"critic_iteration_{iteration}"
                    await self._add_messages_to_thread(
                        task_id=task.id,
                        thread_name=critic_thread_name,
                        messages=[
                            SystemMessage(content=self.critic_instructions),
                            UserMessage(
                                content=f"Please critique the document written by the writer agent. "
                                        f"The task from the user requesting the original document was the following:\n"
                                        f"{task.prompt}\n\n"
                                        f"The latest content from the writer agent is as follows:\n"
                                        f"{latest_content}"
                            )
                        ],
                    )
                    critic_response = await ActionLoop.run(
                        parent_workflow=self,
                        task_id=task.id,
                        thread_name=critic_thread_name,
                        action_registry_key=ActionRegistryKey.CRITIC,
                        model=self.model,
                    )
                    logger.info("Critic tool loop finished")

                    critic_satisfied_completion = await WorkflowHelper.execute_activity(
                        activity_name=ActivityName.ASK_LLM,
                        request=LLMConfig(
                            model=self.model,
                            messages=[
                                UserMessage(
                                    content=f"You're overseeing a project where a writer and a critic are working "
                                            f"together to produce a perfect document. The last message from the critic "
                                            f"was the following: {critic_response}. Please output 'true' if the critic "
                                            f"was satisfied enough for the document to be considered final, otherwise "
                                            f"output 'false' (no quotes, all lowercase) if the writer "
                                            f"needs to make revisions."
                                )
                            ],
                        ),
                        response_type=Completion,
                        start_to_close_timeout=timedelta(seconds=60),
                        retry_policy=RetryPolicy(maximum_attempts=5),
                    )
                    critic_satisfied = critic_satisfied_completion.choices[0].message.content.lower() != "false"
                    iteration += 1
                    content = latest_content
                    if critic_satisfied:
                        final_summary_completion = await WorkflowHelper.execute_activity(
                            activity_name=ActivityName.ASK_LLM,
                            request=LLMConfig(
                                model=self.model,
                                messages=[
                                    UserMessage(
                                        content=f"You're overseeing a project where a writer and a critic are working "
                                                f"together to produce a perfect document. The last message from the "
                                                f"writer was the following:\n{latest_content}\n\n"
                                                f"The output from the critic was the following:\n{critic_response}\n\n"
                                                f"Your final decision was that the document is ready for the user to "
                                                f"review. Please give a thorough explanation of why the writer, "
                                                f"critic, and you all agree that the document is ready for review."
                                    )
                                ],
                            ),
                            response_type=Completion,
                            start_to_close_timeout=timedelta(seconds=60),
                            retry_policy=RetryPolicy(maximum_attempts=5),
                        )

                        final_summary_message = final_summary_completion.choices[0].message.content

                        await self._add_messages_to_thread(
                            task_id=task.id,
                            thread_name=final_responses_thread_name,
                            messages=[
                                AssistantMessage(
                                    content=final_summary_message
                                ),
                            ],
                        )

                if params.require_approval:
                    logger.info("Waiting for instruction or approval")
                    self.waiting_for_instruction = True
                    if self.waiting_for_instruction and not self.task_approved:
                        preface = (
                            f"✅ {self.display_name} has executed the following task: {task.prompt} and is now "
                            f"waiting for your input."
                        )
                        await WorkflowHelper.execute_activity(
                            activity_name=ActivityName.SEND_NOTIFICATION,
                            request=NotificationRequest(
                                topic=agent.name,
                                message=f"{preface}\n\n{self.display_name}:\n{content}",
                                title=self.display_name,
                                tags=["hourglass"],
                            ),
                            response_type=None,
                            start_to_close_timeout=timedelta(seconds=60),
                            retry_policy=RetryPolicy(maximum_attempts=5),
                        )
                    await workflow.wait_condition(lambda: not self.waiting_for_instruction or self.task_approved)
                    if self.task_approved:
                        logger.info("Task approved")
                        break
                    else:
                        logger.info("Task not approved, but instruction received, so continuing")
                        continue
                else:
                    break

            preface = f"🎉 {self.display_name} has completed the following task: {task.prompt}."
            await WorkflowHelper.execute_activity(
                activity_name=ActivityName.SEND_NOTIFICATION,
                request=NotificationRequest(
                    topic=agent.name,
                    message=f"{preface}\n\n{self.display_name}:\n{content}",
                    title=self.display_name,
                    tags=["notification"],
                ),
                response_type=None,
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
            status = "completed"
            self.event_log.append({"event": "task_completed", "status": status})
        except asyncio.CancelledError as error:
            logger.warning(f"Task canceled by user: {task.id}")
            self.event_log.append({"event": "task_canceled", "error": str(error)})
            raise error

        return status

    @staticmethod
    async def _add_messages_to_thread(task_id: str, thread_name: str, messages: List[Message]):
        await WorkflowHelper.execute_activity(
            activity_name=ActivityName.APPEND_MESSAGES_TO_THREAD,
            request=AppendMessagesToThreadParams(
                task_id=task_id,
                thread_name=thread_name,
                messages=messages,
            ),
            response_type=List[Message],
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )

    @staticmethod
    async def _save_artifact(task_id: str, artifact: Artifact):
        await WorkflowHelper.execute_activity(
            activity_name=ActivityName.ADD_ARTIFACT_TO_CONTEXT,
            request=AddArtifactToContextParams(
                task_id=task_id,
                artifact=artifact
            ),
            response_type=None,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )
