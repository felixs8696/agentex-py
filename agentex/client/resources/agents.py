from __future__ import annotations

__all__ = ["AgentsResource", "AsyncAgentsResource"]

from agentex.client.resources._resource import SyncAPIResource, AsyncAPIResource
from agentex.client.types._types import FileTypes
from agentex.client.types.agents import CreateAgentRequest, AgentModel


class AgentsResource(SyncAPIResource):

    def create(
        self,
        *,
        agent_package: FileTypes,
        request: CreateAgentRequest,
    ) -> AgentModel:
        body = {"request": request.to_json()}
        response = self._post(
            "/agents",
            data=body,
            files=[("agent_package", agent_package)],
        )
        response = response.json()
        print("AGENT RESPONSE",
            response
        )
        return AgentModel.from_dict(response)

    def get(self, agent_id: str) -> AgentModel:
        response = self._get(
            f"/agents/{agent_id}",
        )
        response = response.json()
        return AgentModel.from_dict(response)

    def list(self):
        response = self._get(
            "/agents",
        )
        response = response.json()
        return [AgentModel.from_dict(agent) for agent in response]

    def delete(self, agent_name: str) -> None:
        self._delete(
            f"/agents/{agent_name}",
        )


class AsyncAgentsResource(AsyncAPIResource):

    async def create(
        self,
        *,
        agent_package: FileTypes,
        request: CreateAgentRequest,
    ) -> AgentModel:
        body = {"request": request.to_json()}
        response = await self._post(
            "/agents",
            data=body,
            files={"agent_package": agent_package},
        )
        response = response.json()
        return AgentModel.from_dict(response)

    async def get(self, agent_id: str) -> AgentModel:
        response = await self._get(
            f"/agents/{agent_id}",
        )
        response = response.json()
        return AgentModel.from_dict(response)

    async def list(self):
        response = await self._get(
            "/agents",
        )
        response = response.json()
        return [AgentModel.from_dict(agent) for agent in response]

    async def delete(self, agent_name: str) -> None:
        await self._delete(
            f"/agents/{agent_name}",
        )
