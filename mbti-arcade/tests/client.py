from __future__ import annotations

from typing import Any
import anyio

from httpx import ASGITransport, AsyncClient


class SyncASGIClient:
    """Minimal synchronous wrapper built on anyio.run per request."""

    def __init__(self, app) -> None:
        self._transport = ASGITransport(app=app)

    def _request(self, method: str, url: str, **kwargs: Any):
        async def inner():
            async with AsyncClient(transport=self._transport, base_url="http://testserver") as client:
                return await client.request(method, url, **kwargs)

        return anyio.run(inner)

    def get(self, url: str, **kwargs: Any):
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any):
        return self._request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any):
        return self._request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any):
        return self._request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any):
        return self._request("DELETE", url, **kwargs)


def create_client(app) -> SyncASGIClient:
    return SyncASGIClient(app)
