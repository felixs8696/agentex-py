from typing import Union

import httpx
from httpx import Timeout

from agentex.client._client import SyncAPIClient, DEFAULT_TIMEOUT, AsyncAPIClient
from agentex.client.resources.agents import AgentsResource
from agentex.client.resources.tasks import TasksResource
from agentex.constants import AGENTEX_BASE_URL


class Agentex(SyncAPIClient):

    def __init__(
        self,
        *,
        base_url: str | httpx.URL | None = AGENTEX_BASE_URL,
        timeout: Union[float, Timeout] = DEFAULT_TIMEOUT,
    ) -> None:
        """Construct a new synchronous agentex client instance."""

        super().__init__(base_url=base_url, timeout=timeout)

        self.agents = AgentsResource(self)
        self.tasks = TasksResource(self)

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self._client.get(path, **kwargs)


class AsyncAgentex(AsyncAPIClient):

    def __init__(
        self,
        *,
        base_url: str | httpx.URL | None = AGENTEX_BASE_URL,
        timeout: Union[float, Timeout] = DEFAULT_TIMEOUT,
    ) -> None:
        """Construct a new asynchronous agentex client instance."""

        super().__init__(base_url=base_url, timeout=timeout)

        self.agents = AgentsResource(self)
        self.tasks = TasksResource(self)
