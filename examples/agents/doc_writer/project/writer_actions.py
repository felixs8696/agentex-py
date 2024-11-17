from typing import List, Any, Dict, Optional

from pydantic import Field

from agentex.exceptions import ClientError
from agentex.src.entities.actions import ActionResponse, Artifact
from agentex.src.entities.state import ContextKey
from agentex.src.services.action_registry import ActionRegistry, action, ReservedKey
from agentex.src.services.agent_state_service import AgentStateService


class WriterActions(ActionRegistry):

    def __init__(self, agent_state_service: AgentStateService):
        super().__init__()
        self.agent_state_service = agent_state_service

    @action(description="Writes a document in markdown.")
    async def draft_document(
        self,
        document_name: str = Field(
            ...,
            description="The unique name of the document to write"
        ),
        markdown_content: str = Field(
            ...,
            description="The markdown content to write to the document. "
                        "Only output the markdown content itself and nothing else. "
                        "Make sure the markdown is valid and can be rendered properly by any "
                        "basic markdown renderer."),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        try:
            return ActionResponse(
                message=f"Drafted document: {document_name}\n\nContent:\n{markdown_content}",
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to write summary document: {str(e)}",
            )

    @action(description="Revise and perform a self-review on a document.")
    async def revise_document(
        self,
        document_name: str = Field(
            ...,
            description="The unique name of the document to revise"
        ),
        updated_markdown_content: str = Field(
            ...,
            description="The updated markdown content to review. "
                        "Just output the markdown content itself and nothing else. "
                        "Make sure the markdown is valid and can be rendered properly."
        ),
        criticisms_addressed: List[str] = Field(
            ...,
            description="A list of short explanations for how each criticism has been addressed"
        ),
        criticisms_unaddressed: List[str] = Field(
            ...,
            description="A list of short explanations for how each criticism has not been addressed"
        ),
        positive_feedback_preserved: List[str] = Field(
            ...,
            description="A list of positive feedback that was still done well in this revision"
        ),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        if not criticisms_unaddressed:
            return ActionResponse(
                message=f"The document is ready for submission: {document_name}\n\n"
                        f"Content:\n{updated_markdown_content}\n\n"
                        f"Criticisms Addressed:\n{self._format_list(criticisms_addressed)}\n\n"
                        f"Positive Feedback Preserved:\n{self._format_list(positive_feedback_preserved)}",
            )
        else:
            return ActionResponse(
                message=f"The document is not ready for submission: {document_name}\n\n"
                        f"Content:\n{updated_markdown_content}\n\n"
                        f"Criticisms Addressed:\n{self._format_list(criticisms_addressed)}\n\n"
                        f"Criticisms Unaddressed:\n{self._format_list(criticisms_unaddressed)}\n\n"
                        f"Positive Feedback Preserved:\n{self._format_list(positive_feedback_preserved)}",
            )

    @action(
        description="Save artifacts to the agent's context. You must do this in order to hand off anything "
                    "that needs to be reviewed by the critic agent or end user. Make sure to first revise the "
                    "document until all criticisms have been addressed."
    )
    async def save_artifacts(
        self,
        _reserved: Dict[str, Any],
        artifacts: List[Artifact] = Field(
            ...,
            description="A list of artifacts to save to the agent's context."
        ),
    ) -> ActionResponse:
        task_id = _reserved.get(ReservedKey.TASK_ID)
        if not task_id:
            raise ClientError("Task ID not found in the _reserved dictionary and must be provided.")
        await self.agent_state_service.context.batch_set_artifacts(
            task_id=task_id,
            artifacts=artifacts,
            overwrite=True,
        )
        return ActionResponse(
            message=f"Artifacts {[artifact.name for artifact in artifacts]} saved to context."
        )

    @staticmethod
    def _format_list(items: List[str]) -> str:
        return "\n".join([f"- {item}" for item in items])
