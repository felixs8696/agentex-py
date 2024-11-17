from typing import List

from pydantic import Field

from agentex.src.entities.actions import Action, ActionResponse


class DraftDocument(Action):
    """
    Use this tool to write an output document in markdown
    """
    document_name: str = Field(..., description="The unique name of the document to write")
    markdown_content: str = Field(
        ...,
        description="The markdown content to write to the document. "
                    "Just output the markdown content itself and nothing else. "
                    "Make sure the markdown is valid and can be rendered properly."
    )

    async def execute(self) -> ActionResponse:
        try:
            return ActionResponse(
                message=self.markdown_content,
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to write summary document: {str(e)}",
            )


class ReviseDocument(Action):
    """
    Use this tool to do revise and perform a self-review on a document. Use this when a critique is added to the
    message history. Repeat this as needed until all criticisms have been addressed. All positive feedback should be
    preserved.
    """
    document_name: str = Field(..., description="The unique name of the document to revise")
    updated_markdown_content: str = Field(..., description="The updated markdown content to review")
    criticisms_addressed: List[str] = Field(
        ...,
        description="A list of short explanations for how each criticism has been addressed"
    )
    criticisms_unaddressed: List[str] = Field(
        ...,
        description="A list of short explanations for how each criticism has not been addressed"
    )
    positive_feedback_preserved: List[str] = Field(
        ...,
        description="A list of positive feedback that was preserved"
    )

    async def execute(self) -> ActionResponse:
        if not self.criticisms_unaddressed:
            return ActionResponse(
                message=f"The document is ready for submission: {self.document_name}\n\n"
                        f"Content:\n{self.updated_markdown_content}\n\n"
                        f"Criticisms Addressed:\n{self._format_list(self.criticisms_addressed)}\n\n"
                        f"Positive Feedback Preserved:\n{self._format_list(self.positive_feedback_preserved)}",
            )
        else:
            return ActionResponse(
                message=f"The document is not ready for submission: {self.document_name}\n\n"
                        f"Content:\n{self.updated_markdown_content}\n\n"
                        f"Criticisms Addressed:\n{self._format_list(self.criticisms_addressed)}\n\n"
                        f"Criticisms Unaddressed:\n{self._format_list(self.criticisms_unaddressed)}\n\n"
                        f"Positive Feedback Preserved:\n{self._format_list(self.positive_feedback_preserved)}",
            )

    @staticmethod
    def _format_list(items: List[str]) -> str:
        return "\n".join([f"- {item}" for item in items])
