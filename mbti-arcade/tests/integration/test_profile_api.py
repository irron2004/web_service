from __future__ import annotations

from http import HTTPStatus


def test_create_profile_ok(client, auth_headers):
    payload = {
        "display_name": "은하수",
        "avatar_url": "https://example.com/avatar.png",
        "mbti_source": "input",
        "mbti_value": "INFP",
        "show_public": True,
    }

    response = client.post("/v1/profile", json=payload, headers=auth_headers)
    assert response.status_code == HTTPStatus.CREATED

    body = response.json()
    assert body["display_name"] == payload["display_name"]
    assert body["avatar_url"] == payload["avatar_url"]
    assert body["mbti_source"] == payload["mbti_source"]
    assert body["mbti_value"] == payload["mbti_value"]
    assert body["show_public"] is True
    assert "profile_id" in body

    # 동일 토큰으로 self_test 경로로 업데이트하면 MBTI 값이 비워진다.
    update_payload = {
        "display_name": "은하수",
        "avatar_url": "https://cdn.example.com/updated.png",
        "mbti_source": "self_test",
        "show_public": False,
    }

    second = client.post("/v1/profile", json=update_payload, headers=auth_headers)
    assert second.status_code == HTTPStatus.CREATED
    updated = second.json()
    assert updated["avatar_url"] == update_payload["avatar_url"]
    assert updated["mbti_source"] == "self_test"
    assert updated["mbti_value"] is None
    assert updated["show_public"] is False


def test_profile_validation_error(client, auth_headers):
    payload = {
        "display_name": "a",
        "mbti_source": "input",
        "mbti_value": "XXXX",
    }

    response = client.post("/v1/profile", json=payload, headers=auth_headers)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.json()
    assert body["type"].endswith("/validation")
    assert body["status"] == HTTPStatus.UNPROCESSABLE_ENTITY


def test_profile_requires_authorization(client):
    payload = {
        "display_name": "은하수",
        "mbti_source": "self_test",
    }
    response = client.post("/v1/profile", json=payload)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["type"].endswith("/unauthorized")
