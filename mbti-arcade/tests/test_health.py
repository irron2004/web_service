"""Health and readiness probe tests."""

from __future__ import annotations

from typing import Any, Dict

from app.routers import health


def test_healthz_returns_status_and_metadata(client):
    response = client.get("/healthz")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert "uptime_seconds" in payload
    assert payload["service"]
    assert payload["dependencies"] == ["database", "redis"]


def test_readyz_reports_dependency_failures(client, monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)

    response = client.get("/readyz")

    assert response.status_code == 503
    payload: Dict[str, Any] = response.json()
    assert payload["status"] == "degraded"
    assert payload["checks"]["database"]["status"] == "ok"
    assert payload["checks"]["redis"]["status"] == "error"
    assert payload["checks"]["redis"]["detail"] == "REDIS_URL not configured"


def test_readyz_succeeds_when_dependencies_are_healthy(client, monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://test:6379/0")

    async def noop_ping(url: str) -> None:  # pragma: no cover - simple stub
        return None

    monkeypatch.setattr(health, "_ping_redis", noop_ping)

    response = client.get("/readyz")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["checks"]["redis"]["status"] == "ok"
    assert payload["checks"]["database"]["status"] == "ok"
