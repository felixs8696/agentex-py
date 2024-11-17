from typing import List

from pydantic import Field

from agentex.src.entities.actions import Action, ActionResponse


class CritiqueDocument(Action):
    """
    Use this tool to critique the content of a document
    """
    document_name: str = Field(..., description="The unique name of the document to critique")
    criticisms: List[str] = Field(..., description="A list of criticisms for the document")
    positive_feedback: List[str] = Field(..., description="A list of positive feedback for the document")
    score: float = Field(..., description="The score of the document")

    async def execute(self) -> ActionResponse:
        try:
            return ActionResponse(
                message=self._format_full_feedback(),
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to critique document: {str(e)}",
            )

    def _format_full_feedback(self):
        return f"""Critique for Document '{self.document_name}':
- Score: {self.score}
- Critiques:
{self._format_critiques()}
- Positive Feedback:
{self._format_positive_feedback()}
"""

    def _format_critiques(self):
        return "\n".join([f"- {critique}" for critique in self.criticisms])

    def _format_positive_feedback(self):
        return "\n".join([f"- {feedback}" for feedback in self.positive_feedback])


class PassFailDocument(Action):
    """
    Use this tool to pass or fail a document
    """
    document_name: str = Field(..., description="The unique name of the document to pass or fail")
    pass_fail: bool = Field(..., description="Whether the document passed or failed")

    async def execute(self) -> ActionResponse:
        try:
            return ActionResponse(
                message=f"Document '{self.document_name}' {'Passed' if self.pass_fail else 'Failed'}",
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to pass/fail document: {str(e)}",
            )
