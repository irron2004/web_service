import asyncio

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from app.main import HostValidationMiddleware, _load_allowed_hosts


def test_default_allowed_hosts_include_public_domains(monkeypatch):
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
    allowed_hosts = _load_allowed_hosts()

    assert "360me.app" in allowed_hosts
    assert "*.360me.app" in allowed_hosts
    assert "api.360me.app" in allowed_hosts


def test_host_validation_allows_primary_domain():
    app = FastAPI()
    middleware = HostValidationMiddleware(app, allowed_hosts=["*.360me.app", "360me.app"])

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"host", b"api.360me.app")],
        "query_string": b"",
        "server": ("api.360me.app", 443),
        "scheme": "https",
    }
    request = Request(scope)

    async def call_next(req: Request):
        return PlainTextResponse("ok")

    async def run() -> None:
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        assert response.body == b"ok"

    asyncio.run(run())
