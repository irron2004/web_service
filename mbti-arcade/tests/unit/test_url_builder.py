from starlette.requests import Request

from app.urling import build_invite_url


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
    url = build_invite_url(request, token="abc")
    assert "/i/abc" in url
