from fastapi import FastAPI

from app import observability


def test_configure_observability_gracefully_handles_missing_sdk(monkeypatch):
    monkeypatch.setattr(observability, "_INSTRUMENTED", False)
    app = FastAPI()
    assert observability.configure_observability(app) is False
