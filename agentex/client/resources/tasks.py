from __future__ import annotations

__all__ = ["TasksResource", "AsyncTasksResource"]

from typing import Optional

from ._resource import SyncAPIResource, AsyncAPIResource
from ..types.tasks import CreateTaskResponse, ModifyTaskRequest
from ...src.entities.task import TaskModel


class TasksResource(SyncAPIResource):

    def create(
        self,
        *,
        agent_name: str,
        prompt: str,
        require_approval: Optional[bool] = False,
    ) -> CreateTaskResponse:
        response = self._post(
            "/tasks",
            json={
                "agent_name": agent_name,
                "prompt": prompt,
                "require_approval": require_approval,
            },
        )
        response = response.json()
        return CreateTaskResponse.from_dict(response)

    def get(self, task_id: str) -> TaskModel:
        response = self._get(
            f"/tasks/{task_id}",
        )
        response = response.json()
        return TaskModel.from_dict(response)

    def list(self):
        response = self._get(
            "/tasks",
        )
        response = response.json()
        return [TaskModel.from_dict(task) for task in response]

    def delete(self, task_id: str) -> None:
        self._delete(
            f"/tasks/{task_id}",
        )

    def modify(self, task_id: str, modification_request: ModifyTaskRequest) -> None:
        self._post(
            f"/tasks/{task_id}/modify",
            json=modification_request.to_dict(),
        )


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
        return CreateTaskResponse.from_dict(response)

    async def get(self, task_id: str) -> TaskModel:
        response = await self._get(
            f"/tasks/{task_id}",
        )
        response = response.json()
        return TaskModel.from_dict(response)

    async def list(self):
        response = await self._get(
            "/tasks",
        )
        response = response.json()
        return [TaskModel.from_dict(task) for task in response]

    async def delete(self, task_id: str) -> None:
        await self._delete(
            f"/tasks/{task_id}",
        )

    async def modify(self, task_id: str, modification_request: ModifyTaskRequest) -> None:
        await self._post(
            f"/tasks/{task_id}/modify",
            json=modification_request.to_dict(),
        )
