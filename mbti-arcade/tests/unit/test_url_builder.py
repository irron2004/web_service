from starlette.requests import Request

from app import urling


def test_build_invite_url_uses_url_for(app):
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "root_path": "",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 0),
        "server": ("testserver", 80),
        "app": app,
    }
    scope["router"] = app.router
    request = Request(scope)
    url = urling.build_invite_url(request, token="abc")
    assert "/i/abc" in url


def test_build_invite_url_canonicalizes_with_base(app, monkeypatch):
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "root_path": "",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 0),
        "server": ("testserver", 80),
        "app": app,
    }
    scope["router"] = app.router
    request = Request(scope)

    monkeypatch.setattr(
        urling.settings,
        "CANONICAL_BASE_URL",
        "https://webservice-production-c039.up.railway.app",
    )

    result = urling.build_invite_url(request, token="xyz")
    assert result.startswith("https://webservice-production-c039.up.railway.app")
    assert result.endswith("/i/xyz")
