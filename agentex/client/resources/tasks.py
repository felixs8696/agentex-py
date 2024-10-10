# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

__all__ = ["TasksResource", "AsyncTasksResource"]

from ._resource import SyncAPIResource, AsyncAPIResource
from ..types.tasks import CreateTaskResponse, GetTaskResponse

"""
class AgentsResource(SyncAPIResource):

    def create(
        self,
        *,
        agent_package: FileTypes,
        request: CreateAgentRequest,
    ) -> CreateAgentResponse:
        body = {"request": json.dumps(request)}
        response = self._post(
            "/agents",
            body=body,
            files=[("agent_package", agent_package)],
            headers={"Content-Type": "multipart/form-data"},
        )
        return CreateAgentResponse.from_json(response.json())


class AsyncAgentsResource(AsyncAPIResource):

    async def create(
        self,
        *,
        agent_package: FileTypes,
        request: CreateAgentRequest,
    ) -> CreateAgentResponse:
        body = {"request": json.dumps(request)}
        response = await self._post(
            "/agents",
            body=body,
            files=[("agent_package", agent_package)],
            headers={"Content-Type": "multipart/form-data"},
        )
        return CreateAgentResponse.from_json(response.json())
"""


class TasksResource(SyncAPIResource):

    def create(
        self,
        *,
        agent: str,
        prompt: str,
    ) -> CreateTaskResponse:
        response = self._post(
            "/tasks",
            body={
                "agent": agent,
                "prompt": prompt,
            },
        )
        return CreateTaskResponse.from_json(response.json())

    def get(self, task_id: str) -> GetTaskResponse:
        response = self._get(
            f"/tasks/{task_id}",
        )
        return GetTaskResponse.from_json(response.json())


class AsyncTasksResource(AsyncAPIResource):

    async def create(
        self,
        *,
        agent: str,
        prompt: str,
    ) -> CreateTaskResponse:
        response = await self._post(
            "/tasks",
            body={
                "agent": agent,
                "prompt": prompt,
            },
        )
        return CreateTaskResponse.from_json(response.json())

    async def get(self, task_id: str) -> GetTaskResponse:
        response = await self._get(
            f"/tasks/{task_id}",
        )
        return GetTaskResponse.from_json(response.json())
