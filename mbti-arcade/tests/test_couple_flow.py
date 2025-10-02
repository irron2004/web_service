from __future__ import annotations

from app.couple.constants import QUESTION_REGISTRY


def _create_session(client) -> dict:
    response = client.post(
        "/api/couples/sessions",
        json={
            "participants": [
                {"role": "A", "nickname": "민지"},
                {"role": "B", "nickname": "준호"},
            ],
            "stage1_snapshot": {"k": 2, "visible": False, "dimensions": {"CS": 3.1}},
        },
    )
    assert response.status_code == 201
    return response.json()

def _answers(offset: int = 0) -> list[dict]:
    items = []
    for idx, code in enumerate(sorted(QUESTION_REGISTRY)):
        base = (idx + offset) % 5
        if code == "CS2":
            base = 1  # trigger safety flag when combined
        items.append({"code": code, "value": base})
    return items

def test_compute_requires_all_participants(client):
    session = _create_session(client)
    token_a = next(p["access_token"] for p in session["participants"] if p["role"] == "A")

    # Only participant A submits responses.
    response = client.put(
        f"/api/couples/sessions/{session['session_id']}/responses",
        json={
            "access_token": token_a,
            "self_answers": _answers(),
            "guess_answers": _answers(offset=1),
            "stage": 2,
        },
    )
    assert response.status_code == 200

    compute = client.post(
        f"/api/couples/sessions/{session['session_id']}/compute",
        json={"access_token": token_a},
    )
    assert compute.status_code == 409
    body = compute.json()
    assert body["type"].endswith("/stage-incomplete")

def test_full_couple_flow_computes_result_and_packet(client):
    session = _create_session(client)
    session_id = session["session_id"]
    token_a = next(p["access_token"] for p in session["participants"] if p["role"] == "A")
    token_b = next(p["access_token"] for p in session["participants"] if p["role"] == "B")

    # Stage1 snapshot updated with k>=3 to unlock visibility.
    stage1 = client.patch(
        f"/api/couples/sessions/{session_id}/stage1",
        json={"k": 5, "visible": True, "dimensions": {"CS": 3.2, "EA": 2.9}},
    )
    assert stage1.status_code == 200
    k_state = stage1.json()["k_state"]
    assert k_state["visible"] is True
    assert k_state["current"] == 5
    assert k_state["threshold"] == 3
    assert stage1.json()["stage"] >= 1

    # Participant A submissions.
    resp_a = client.put(
        f"/api/couples/sessions/{session_id}/responses",
        json={
            "access_token": token_a,
            "self_answers": _answers(),
            "guess_answers": _answers(offset=1),
            "stage": 2,
        },
    )
    assert resp_a.status_code == 200
    assert resp_a.json()["self_completed"] is True

    saved_a = client.get(
        f"/api/couples/sessions/{session_id}/responses",
        params={"access_token": token_a},
    )
    assert saved_a.status_code == 200
    assert len(saved_a.json()["self_answers"]) == len(QUESTION_REGISTRY)

    # Participant B submissions.
    resp_b = client.put(
        f"/api/couples/sessions/{session_id}/responses",
        json={
            "access_token": token_b,
            "self_answers": _answers(offset=2),
            "guess_answers": _answers(offset=3),
            "stage": 2,
        },
    )
    assert resp_b.status_code == 200

    # Compute final result (token validation requires participant token).
    compute = client.post(
        f"/api/couples/sessions/{session_id}/compute",
        json={"access_token": token_a},
    )
    assert compute.status_code == 200
    body = compute.json()

    assert body["session_id"] == session_id
    assert body["k_state"]["visible"] is True
    assert body["k_state"]["current"] >= body["k_state"]["threshold"]
    assert body["decision_packet"]["packet_sha256"]
    assert body["decision_packet"]["created_at"]
    assert body["decision_packet"]["code_ref"] is not None
    assert body["gap_summary"]["grade"] in {"green", "amber", "red"}
    assert len(body["flags"]) >= 1
    assert len(body["insights"]) <= 3
    assert len(body["top_delta_items"]) > 0
    assert body["generated_at"]


def test_responses_invalid_payload_rolls_back(client):
    session = _create_session(client)
    session_id = session["session_id"]
    token_a = next(p["access_token"] for p in session["participants"] if p["role"] == "A")

    invalid_answers = _answers()
    invalid_answers.append({"code": "INVALID", "value": 3})

    response = client.put(
        f"/api/couples/sessions/{session_id}/responses",
        json={
            "access_token": token_a,
            "self_answers": invalid_answers,
            "guess_answers": _answers(offset=1),
            "stage": 2,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["type"].endswith("/question-invalid")

    saved = client.get(
        f"/api/couples/sessions/{session_id}/responses",
        params={"access_token": token_a},
    )
    assert saved.status_code == 200
    payload = saved.json()
    assert payload["self_answers"] == {}
    assert payload["guess_answers"] == {}


def test_responses_reject_duplicate_entries(client):
    session = _create_session(client)
    session_id = session["session_id"]
    token_a = next(p["access_token"] for p in session["participants"] if p["role"] == "A")

    answers = _answers()
    answers.append(answers[0])

    response = client.put(
        f"/api/couples/sessions/{session_id}/responses",
        json={
            "access_token": token_a,
            "self_answers": answers,
            "guess_answers": _answers(offset=1),
            "stage": 2,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["type"].endswith("/duplicate-answer")


def test_responses_prevent_stage_regression(client):
    session = _create_session(client)
    session_id = session["session_id"]
    token_a = next(p["access_token"] for p in session["participants"] if p["role"] == "A")

    client.put(
        f"/api/couples/sessions/{session_id}/responses",
        json={
            "access_token": token_a,
            "self_answers": _answers(),
            "guess_answers": _answers(offset=1),
            "stage": 2,
        },
    )

    regression = client.put(
        f"/api/couples/sessions/{session_id}/responses",
        json={
            "access_token": token_a,
            "self_answers": _answers(),
            "guess_answers": _answers(offset=1),
            "stage": 1,
        },
    )

    assert regression.status_code == 422


def test_responses_prevent_stage_skip(client):
    session = _create_session(client)
    session_id = session["session_id"]
    token_a = next(p["access_token"] for p in session["participants"] if p["role"] == "A")

    response = client.put(
        f"/api/couples/sessions/{session_id}/responses",
        json={
            "access_token": token_a,
            "self_answers": _answers(),
            "guess_answers": _answers(offset=1),
            "stage": 3,
        },
    )

    assert response.status_code == 409
    assert response.json()["type"].endswith("/stage-order")
