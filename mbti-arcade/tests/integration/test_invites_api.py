from __future__ import annotations

from datetime import datetime, timedelta, timezone

from http import HTTPStatus

from app.database import session_scope
from app.models import Participant, Session as SessionModel, ParticipantRelation


PROFILE_PAYLOAD = {
    "display_name": "은하수",
    "avatar_url": "https://example.com/avatar.png",
    "mbti_source": "input",
    "mbti_value": "INFP",
    "show_public": True,
}


def create_profile(client, auth_headers):
    response = client.post("/v1/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
    assert response.status_code == HTTPStatus.CREATED


def test_invite_issue_and_render(client, auth_headers):
    create_profile(client, auth_headers)

    response = client.post(
        "/v1/invites",
        json={"expires_in_days": 7, "max_raters": 5},
        headers=auth_headers,
    )
    assert response.status_code == HTTPStatus.CREATED

    body = response.json()
    token = body["invite_token"]
    assert body["invite_url"] == (
        f"https://webservice-production-c039.up.railway.app/i/{token}"
    )
    assert body["owner_display_name"] == PROFILE_PAYLOAD["display_name"]
    assert body["owner_avatar_url"] == PROFILE_PAYLOAD["avatar_url"]

    page = client.get(f"/i/{token}")
    assert page.status_code == HTTPStatus.OK
    content = page.text
    assert PROFILE_PAYLOAD["display_name"] in content


def test_invite_expired_returns_problem_detail(client, auth_headers):
    create_profile(client, auth_headers)
    response = client.post(
        "/v1/invites",
        json={"expires_in_days": 1, "max_raters": 5},
        headers=auth_headers,
    )
    data = response.json()
    token = data["invite_token"]
    session_id = data["session_id"]
    assert data["invite_url"] == (
        f"https://webservice-production-c039.up.railway.app/i/{token}"
    )

    with session_scope() as db:
        session = db.get(SessionModel, session_id)
        session.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

    expired = client.get(f"/i/{token}")
    assert expired.status_code == HTTPStatus.GONE
    body = expired.json()
    assert body["type"].endswith("/invite-expired")


def test_invite_capacity_returns_problem_detail(client, auth_headers):
    create_profile(client, auth_headers)
    response = client.post(
        "/v1/invites",
        json={"expires_in_days": 3, "max_raters": 1},
        headers=auth_headers,
    )
    data = response.json()
    token = data["invite_token"]
    session_id = data["session_id"]
    assert data["invite_url"] == (
        f"https://webservice-production-c039.up.railway.app/i/{token}"
    )

    with session_scope() as db:
        participant = Participant(
            session_id=session_id,
            invite_token=token,
            relation=ParticipantRelation.FRIEND,
            display_name="친구",
            consent_display=False,
        )
        db.add(participant)

    full = client.get(f"/i/{token}")
    assert full.status_code == HTTPStatus.TOO_MANY_REQUESTS
    body = full.json()
    assert body["type"].endswith("/invite-capacity")
