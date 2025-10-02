# 파일: mbti-arcade/tests/test_responses_api.py

from app.data.questions import questions_for_mode


def _create_session(client, mode: str = "basic") -> dict:
    response = client.post(
        "/api/sessions",
        json={"mode": mode},
    )
    assert response.status_code == 201
    return response.json()


def _build_answers(mode: str) -> list[dict[str, int]]:
    questions = questions_for_mode(mode)
    return [{"question_id": q["id"], "value": 3} for q in questions]

def test_submit_self_success(client):
    session = _create_session(client)
    answers = _build_answers("basic")

    response = client.post(
        "/api/self/submit",
        json={"session_id": session["session_id"], "answers": answers},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session["session_id"]
    assert set(body["self_norm"].keys()) == {"EI", "SN", "TF", "JP"}

def test_submit_self_missing_question_returns_problem_details(client):
    session = _create_session(client)
    answers = _build_answers("basic")
    answers.pop()  # remove one question to trigger validation failure

    response = client.post(
        "/api/self/submit",
        json={"session_id": session["session_id"], "answers": answers},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["type"].endswith("/answers-invalid")
    assert "answers" in body["errors"]
    assert any("누락된 문항" in message for message in body["errors"]["answers"])

def test_submit_other_invalid_answers_rejected(client):
    session = _create_session(client)
    base_answers = _build_answers("basic")

    # Self responses must exist first
    self_response = client.post(
        "/api/self/submit",
        json={"session_id": session["session_id"], "answers": base_answers},
    )
    assert self_response.status_code == 200

    # Duplicate question id to trigger validation
    invalid_answers = base_answers.copy()
    invalid_answers[1] = invalid_answers[0]

    response = client.post(
        "/api/other/submit",
        json={
            "invite_token": session["invite_token"],
            "answers": invalid_answers,
            "relation_tag": "friend",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["type"].endswith("/answers-invalid")
    assert any("중복 문항" in message for message in body["errors"]["answers"])

def test_submit_other_success_updates_respondents(client):
    session = _create_session(client)
    answers = _build_answers("basic")

    # Self baseline
    client.post(
        "/api/self/submit",
        json={"session_id": session["session_id"], "answers": answers},
    )

    response = client.post(
        "/api/other/submit",
        json={
            "invite_token": session["invite_token"],
            "answers": answers,
            "relation_tag": "friend",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["session_id"] == session["session_id"]
    assert body["respondents"] >= 1


def test_submit_self_unknown_session_returns_problem_details(client):
    response = client.post(
        "/api/self/submit",
        json={
            "session_id": "missing-session",
            "answers": [],
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["type"].endswith("/session-not-found")
    assert body["title"] == "Session Not Found"


def test_submit_other_unknown_invite_returns_problem_details(client):
    response = client.post(
        "/api/other/submit",
        json={
            "invite_token": "missing-token",
            "answers": [{"question_id": 1, "value": 3}],
            "relation_tag": "friend",
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["type"].endswith("/invite-not-found")
    assert body["title"] == "Invite Not Found"
