from __future__ import annotations

from app.data.questions import questions_for_mode


def _create_session(client, mode: str = "basic") -> dict:
    response = client.post("/api/sessions", json={"mode": mode})
    assert response.status_code == 201
    return response.json()


def _answers(mode: str = "basic") -> list[dict[str, int]]:
    return [{"question_id": item["id"], "value": 3} for item in questions_for_mode(mode)]


def _submit_self(client, session_id: str, mode: str = "basic") -> None:
    response = client.post(
        "/api/self/submit",
        json={"session_id": session_id, "answers": _answers(mode)},
    )
    assert response.status_code == 200


def _submit_other(client, invite_token: str, *, rater_key: str) -> None:
    payload = {
        "invite_token": invite_token,
        "relation_tag": "friend",
        "rater_key": rater_key,
        "answers": _answers("basic"),
    }
    response = client.post("/api/other/submit", json=payload)
    assert response.status_code in {200, 201}


def test_fetch_result_missing_session_returns_problem_details(client):
    response = client.get("/api/result/missing-token")
    assert response.status_code == 404
    body = response.json()
    assert body["type"].endswith("/invite-not-found")
    assert body["title"] == "Invite Not Found"


def test_fetch_result_enforces_k_threshold_before_and_after_unlock(client):
    session = _create_session(client)
    _submit_self(client, session["session_id"])

    # With only self answers, other details must stay locked.
    result_locked = client.get(f"/api/result/{session['invite_token']}")
    assert result_locked.status_code == 200
    locked_body = result_locked.json()
    assert locked_body["n"] == 0
    assert locked_body["other_norm"] is None
    assert locked_body["gap"] is None
    assert locked_body["gap_score"] is None

    # Add two friend submissions (still below k threshold).
    _submit_other(client, session["invite_token"], rater_key="r1")
    _submit_other(client, session["invite_token"], rater_key="r2")

    result_guarded = client.get(f"/api/result/{session['invite_token']}")
    assert result_guarded.status_code == 200
    guarded_body = result_guarded.json()
    assert guarded_body["n"] == 2
    assert guarded_body["other_norm"] is None
    assert guarded_body["gap"] is None

    # Third submission should unlock aggregate disclosure.
    _submit_other(client, session["invite_token"], rater_key="r3")
    result_unlocked = client.get(f"/api/result/{session['invite_token']}")
    assert result_unlocked.status_code == 200
    unlocked_body = result_unlocked.json()
    assert unlocked_body["n"] == 3
    assert unlocked_body["other_norm"] is not None
    assert unlocked_body["gap"] is not None
    assert unlocked_body["gap_score"] is not None
