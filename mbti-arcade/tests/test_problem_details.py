# 파일: mbti-arcade/tests/test_problem_details.py
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
