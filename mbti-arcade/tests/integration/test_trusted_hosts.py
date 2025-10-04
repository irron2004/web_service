from http import HTTPStatus
from urllib.parse import parse_qs, urlparse


def test_allowed_host_passes(client):
    response = client.get("/mbti/friend", headers={"host": "api.360me.app"})
    assert response.status_code == HTTPStatus.OK


def test_wildcard_subdomain_allowed(client):
    response = client.get("/mbti/friend", headers={"host": "sub.api.360me.app"})
    assert response.status_code == HTTPStatus.OK


def test_unallowed_host_blocked(client):
    response = client.get("http://evil.example.com/mbti/friend")
    assert response.status_code in {HTTPStatus.BAD_REQUEST, HTTPStatus.MISDIRECTED_REQUEST}


def test_https_scheme_enforced(client, monkeypatch):
    def _fake_create_pair(self, *args, **kwargs):
        return "pair-id"

    def _fake_issue_token(pair_id, my_mbti):
        return "stub-token"

    monkeypatch.setattr(
        "app.core.services.mbti_service.MBTIService.create_pair",
        _fake_create_pair,
    )
    monkeypatch.setattr("app.core.token.issue_token", _fake_issue_token)

    response = client.post(
        "http://api.360me.app/share",
        data={"name": "Alice", "email": "", "my_mbti": "INTJ"},
        headers={"x-forwarded-proto": "http"},
        follow_redirects=False,
    )
    assert response.status_code == HTTPStatus.SEE_OTHER
    location = response.headers.get("location", "")
    assert location
    parsed = urlparse(location)
    query_params = parse_qs(parsed.query)
    share_urls = query_params.get("url", [])
    assert share_urls
    assert share_urls[0].startswith("https://")
