import os
from typing import Union

import httpx
from httpx import Timeout

DEFAULT_TIMEOUT = httpx.Timeout(timeout=60.0, connect=5.0)
DEFAULT_MAX_RETRIES = 2


class SyncAPIClient:
    def __init__(
        self,
        *,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout] = DEFAULT_TIMEOUT,
    ) -> None:
        """Construct a new synchronous agentex client instance."""
        if base_url is None:
            self.base_url = os.environ.get("AGENTEX_BASE_URL")
        if base_url is None:
            self.base_url = f"http://localhost:5003/"

        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
        )

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self._client.get(path, **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self._client.post(path, **kwargs)

    def patch(self, path: str, **kwargs) -> httpx.Response:
        return self._client.patch(path, **kwargs)

    def put(self, path: str, **kwargs) -> httpx.Response:
        return self._client.put(path, **kwargs)

    def delete(self, path: str, **kwargs) -> httpx.Response:
        return self._client.delete(path, **kwargs)


class AsyncAPIClient:
    def __init__(
        self,
        *,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout] = DEFAULT_TIMEOUT,
    ) -> None:
        """Construct a new asynchronous agentex client instance."""
        if base_url is None:
            self.base_url = os.environ.get("AGENTEX_BASE_URL")
        if base_url is None:
            self.base_url = f"http://localhost:5003/"

        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
        )

    async def get(self, path: str, **kwargs) -> httpx.Response:
        return await self._client.get(path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        return await self._client.post(path, **kwargs)

    async def patch(self, path: str, **kwargs) -> httpx.Response:
        return await self._client.patch(path, **kwargs)

    async def put(self, path: str, **kwargs) -> httpx.Response:
        return await self._client.put(path, **kwargs)

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        return await self._client.delete(path, **kwargs)
