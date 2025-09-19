from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz_returns_ok_status():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_returns_ready_status():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
