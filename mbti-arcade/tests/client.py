"""Blocking portal-backed httpx client for synchronous test execution."""
from __future__ import annotations

from typing import Any

from anyio.from_thread import BlockingPortal, start_blocking_portal
from httpx import ASGITransport, AsyncClient, Response

DEFAULT_BASE_URL = "http://testserver"


async def _open_client(
    app,
    base_url: str,
    follow_redirects: bool,
    kwargs: dict[str, Any],
) -> AsyncClient:
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url=base_url,
        follow_redirects=follow_redirects,
        **kwargs,
    )
    await client.__aenter__()
    return client


async def _close_client(client: AsyncClient) -> None:
    await client.__aexit__(None, None, None)


async def _dispatch_request(
    client: AsyncClient, method: str, url: str, kwargs: dict[str, Any]
) -> Response:
    return await client.request(method, url, **kwargs)


class SyncASGIClient:
    def __init__(
        self,
        app,
        *,
        base_url: str = DEFAULT_BASE_URL,
        follow_redirects: bool = True,
        **kwargs: Any,
    ) -> None:
        self._portal_cm = start_blocking_portal()
        self._portal: BlockingPortal | None = self._portal_cm.__enter__()
        self._client: AsyncClient | None = self._portal.call(
            _open_client,
            app,
            base_url,
            follow_redirects,
            kwargs,
        )

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        assert self._portal is not None and self._client is not None
        return self._portal.call(
            _dispatch_request,
            self._client,
            method,
            url,
            kwargs,
        )

    def get(self, url: str, **kwargs: Any) -> Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Response:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        if self._portal is None or self._client is None:
            return
        try:
            self._portal.call(_close_client, self._client)
        finally:
            self._portal_cm.__exit__(None, None, None)
            self._portal = None
            self._client = None


def create_client(
    app,
    *,
    base_url: str = DEFAULT_BASE_URL,
    follow_redirects: bool = True,
    **kwargs: Any,
) -> SyncASGIClient:
    return SyncASGIClient(
        app,
        base_url=base_url,
        follow_redirects=follow_redirects,
        **kwargs,
    )
