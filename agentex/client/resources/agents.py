# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import json

__all__ = ["AgentsResource", "AsyncAgentsResource"]

from agentex.client.resources._resource import SyncAPIResource, AsyncAPIResource
from agentex.client.types._types import FileTypes
from agentex.client.types.agents import CreateAgentRequest, CreateAgentResponse


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
        )
        response = response.json()
        print(json.dumps(response, indent=2))
        return CreateAgentResponse.from_dict(response)


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
            files={"agent_package": agent_package},
        )
        response = response.json()
        print(json.dumps(response, indent=2))
        return CreateAgentResponse.from_dict(response)
