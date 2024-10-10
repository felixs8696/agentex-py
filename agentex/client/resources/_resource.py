from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentex.client.agentex import Agentex, AsyncAgentex


class SyncAPIResource:

    def __init__(self, client: Agentex) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._put = client.put
        self._delete = client.delete


class AsyncAPIResource:

    def __init__(self, client: AsyncAgentex) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._put = client.put
        self._delete = client.delete
