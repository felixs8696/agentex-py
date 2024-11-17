from typing import List, Dict, Any, Optional

from pydantic import Field

from agentex.exceptions import ClientError
from agentex.src.entities.actions import ActionResponse, Artifact
from agentex.src.services.action_registry import ActionRegistry, action, ReservedKey
from agentex.src.services.agent_state_service import AgentStateService


class CriticActions(ActionRegistry):

    def __init__(self, agent_state_service: AgentStateService):
        super().__init__()
        self.agent_state_service = agent_state_service

    @action(description="Critique the content of a document, providing both criticisms and positive feedback.")
    async def critique_document(
        self,
        document_name: str = Field(
            ...,
            description="The unique name of the document to critique"
        ),
        criticisms: List[str] = Field(
            ...,
            description="A list of short, but specific and actionable criticisms for the document"
        ),
        positive_feedback: List[str] = Field(
            ...,
            description="A list of short, but specific positive feedback for the document"
        ),
        score: int = Field(
            ...,
            description="A score between 0 and 100 that represents the quality of the document"
                        "(0 being the worst and 100 being the best)"
        ),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        try:
            message = self._format_full_feedback(document_name, criticisms, positive_feedback, score)
            return ActionResponse(message=message)
        except Exception as e:
            return ActionResponse(message=f"Failed to critique document: {str(e)}")

    @action(description="Pass or fail a document based on its quality.")
    async def pass_fail_document(
        self,
        document_name: str = Field(
            ...,
            description="The unique name of the document to pass or fail"
        ),
        pass_fail: bool = Field(
            ...,
            description="Whether the document passed or failed the quality check"
        ),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        try:
            status = 'Passed' if pass_fail else 'Failed'
            return ActionResponse(message=f"Document '{document_name}' {status}")
        except Exception as e:
            return ActionResponse(message=f"Failed to pass/fail document: {str(e)}")

    @action(description="Retrieve artifacts from the agent's context by unique name. If documents or artifacts are "
                        "referenced by name, look them up with this tool.")
    async def get_artifacts(
        self,
        _reserved: Dict[str, Any],
        artifact_names: List[str] = Field(
            ...,
            description="A list of unique names of the artifacts to retrieve from the agent's context"
        ),
    ) -> ActionResponse:
        task_id = _reserved.get(ReservedKey.TASK_ID)
        if not task_id:
            raise ClientError("Task ID not found in the _reserved dictionary and must be provided.")
        artifacts_dict = await self.agent_state_service.context.get_artifacts(task_id=task_id)
        artifacts_retrieved = {name: artifacts_dict.get(name) for name in artifact_names}
        missing_artifacts = [name for name, artifact in artifacts_retrieved.items() if not artifact]
        artifacts_found_response = self._format_artifact_responses(artifacts_retrieved)

        final_response = ""
        if artifacts_found_response:
            final_response += f"Artifacts found:\n{artifacts_found_response}\n\n----\n\n"

        if missing_artifacts:
            final_response += f"The following artifacts were not found:\n{self._format_list(missing_artifacts)}\n\n"
            final_response += (f"I only have access to the following artifacts:\n"
                               f"{self._format_list(list(artifacts_dict.keys()))}. If you meant one of these, please "
                               f"request it using its exact name.")

        return ActionResponse(
            message=final_response
        )

    @staticmethod
    def _format_artifact_responses(artifacts_retrieved: Dict[str, Artifact]) -> str:
        response = ""
        for name, artifact in artifacts_retrieved.items():
            if artifact:
                response += f"Artifact '{artifact.name}':\n"
                response += f"- Description: {artifact.description}\n"
                response += f"- Content: {artifact.content}\n"
                response += "\n"
        return response

    @staticmethod
    def _format_list(items: List[str]) -> str:
        return "\n".join([f"- {item}" for item in items])

    @staticmethod
    def _format_full_feedback(
        document_name: str,
        criticisms: List[str],
        positive_feedback: List[str],
        score: float
    ) -> str:
        return (
            f"Critique for Document '{document_name}':\n"
            f"- Score: {score}\n"
            f"- Critiques:\n{CriticActions._format_list(criticisms)}\n"
            f"- Positive Feedback:\n{CriticActions._format_list(positive_feedback)}"
        )
