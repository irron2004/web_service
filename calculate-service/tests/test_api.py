from fastapi.testclient import TestClient

from app import create_app
from app.problem_bank import list_categories


client = TestClient(create_app())


def test_health_endpoint_returns_status() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"


def test_default_problem_category_is_returned() -> None:
    response = client.get("/api/problems")
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == list_categories()[0]
    assert body["total"] == len(body["items"])


def test_invalid_category_returns_problem_detail() -> None:
    response = client.get("/api/problems", params={"category": "INVALID"})
    assert response.status_code == 404
    body = response.json()
    assert body["type"].endswith("invalid-category")
    assert body["status"] == 404


def test_request_id_is_preserved() -> None:
    request_id = "test-request-id"
    response = client.get("/api/problems", headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_html_routes_emit_noindex_header() -> None:
    response = client.get("/problems")
    assert response.status_code == 200
    assert response.headers["X-Robots-Tag"] == "noindex"
