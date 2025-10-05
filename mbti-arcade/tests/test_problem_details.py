# 파일: mbti-arcade/tests/test_problem_details.py
from app.core.config import REQUEST_ID_HEADER


def test_not_found_returns_problem_details_payload(client):
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert body["detail"] == "Not Found"
    assert body["instance"] == "/non-existent-route"
    assert body["type"].endswith("/http-404")

def test_validation_error_returns_problem_details_payload(client):
    response = client.post("/api/sessions", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == 422
    assert body["title"] == "Validation Failed"
    assert body["type"].endswith("/validation")
    assert "mode" in body["errors"]
    assert any("Field required" in message for message in body["errors"]["mode"])
    assert body["detail"].startswith("요청 본문을 검증할 수 없습니다")


def test_unhandled_error_returns_problem_details_and_request_id(app, client):
    async def boom() -> None:
        raise RuntimeError("boom")

    # FastAPI ensures routes are appended; clean up after the test to avoid leakage.
    app.router.add_api_route("/boom", boom, methods=["GET"])

    try:
        response = client.get("/boom")
        assert response.status_code == 500
        body = response.json()
        assert body["status"] == 500
        assert body["title"] == "Internal Server Error"
        assert body["detail"].startswith("예상치 못한 오류")
        assert body["instance"] == "/boom"
        request_id = response.headers.get(REQUEST_ID_HEADER)
        assert request_id

        provided = "req-error-test"
        response_with_header = client.get(
            "/boom", headers={REQUEST_ID_HEADER: provided}
        )
        assert response_with_header.status_code == 500
        assert response_with_header.headers.get(REQUEST_ID_HEADER) == provided
    finally:
        # Remove the temporary route to avoid polluting other tests.
        app.router.routes.pop()
