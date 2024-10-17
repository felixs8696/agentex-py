# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

__all__ = ["TasksResource", "AsyncTasksResource"]

import json

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
        body = {"request": request.to_json()}
        response = self._post(
            "/agents",
            data=body,
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
        body = {"request": request.to_json()}
        response = await self._post(
            "/agents",
            data=body,
            files=[("agent_package", agent_package)],
            headers={"Content-Type": "multipart/form-data"},
        )
        return CreateAgentResponse.from_json(response.json())
"""


class TasksResource(SyncAPIResource):

    def create(
        self,
        *,
        agent_name: str,
        agent_version: str,
        prompt: str,
    ) -> CreateTaskResponse:
        response = self._post(
            "/tasks",
            json={
                "agent_name": agent_name,
                "agent_version": agent_version,
                "prompt": prompt,
            },
        )
        response = response.json()
        print(json.dumps(response, indent=2))
        return CreateTaskResponse.from_dict(response)

    def get(self, task_id: str) -> GetTaskResponse:
        response = self._get(
            f"/tasks/{task_id}",
        )
        response = response.json()
        print(json.dumps(response, indent=2))
        return GetTaskResponse.from_dict(response)


class AsyncTasksResource(AsyncAPIResource):

    async def create(
        self,
        *,
        agent: str,
        prompt: str,
    ) -> CreateTaskResponse:
        response = await self._post(
            "/tasks",
            json={
                "agent": agent,
                "prompt": prompt,
            },
        )
        response = response.json()
        print(json.dumps(response, indent=2))
        return CreateTaskResponse.from_dict(response)

    async def get(self, task_id: str) -> GetTaskResponse:
        response = await self._get(
            f"/tasks/{task_id}",
        )
        response = response.json()
        print(json.dumps(response, indent=2))
        return GetTaskResponse.from_dict(response)
