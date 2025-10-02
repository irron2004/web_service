from app.utils.privacy import NOINDEX_VALUE
from app.data.questions import questions_for_mode


def _create_session(client, mode: str = "basic") -> dict:
    response = client.post("/api/sessions", json={"mode": mode})
    assert response.status_code == 201
    return response.json()


def _build_answers(mode: str) -> list[dict[str, int]]:
    questions = questions_for_mode(mode)
    return [{"question_id": question["id"], "value": 3} for question in questions]


def test_share_success_sets_noindex_header_and_meta(client):
    response = client.get("/mbti/share_success", params={"url": "https://example.com"})
    assert response.status_code == 200
    assert response.headers.get("X-Robots-Tag") == NOINDEX_VALUE
    assert 'name="robots"' in response.text
    assert NOINDEX_VALUE in response.text


def test_api_result_endpoint_sets_noindex_header(client):
    session = _create_session(client)
    answers = _build_answers("basic")

    submit = client.post(
        "/api/self/submit",
        json={"session_id": session["session_id"], "answers": answers},
    )
    assert submit.status_code == 200

    result = client.get(f"/api/result/{session['invite_token']}")
    assert result.status_code == 200
    assert result.headers.get("X-Robots-Tag") == NOINDEX_VALUE


def _build_form_payload(mode: str = "basic") -> dict[str, str]:
    return {f"q{item['id']}": "3" for item in questions_for_mode(mode)}


def test_share_form_sets_noindex_header_and_meta(client):
    response = client.get("/mbti/share")
    assert response.status_code == 200
    assert response.headers.get("X-Robots-Tag") == NOINDEX_VALUE
    assert 'name="robots"' in response.text
    assert NOINDEX_VALUE in response.text


def test_self_result_page_sets_noindex_header(client):
    payload = _build_form_payload()
    response = client.post("/mbti/result", data=payload)
    assert response.status_code == 200
    assert response.headers.get("X-Robots-Tag") == NOINDEX_VALUE
