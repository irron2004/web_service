from __future__ import annotations

import pytest
from fastapi import FastAPI

from app.main import app as fastapi_app
from .client import create_client


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """FastAPI 앱 인스턴스를 세션 전역으로 공유."""

    return fastapi_app


@pytest.fixture
def client(app: FastAPI):
    """FastAPI 앱에 대한 동기 HTTP 클라이언트."""

    test_client = create_client(app)
    try:
        yield test_client
    finally:
        test_client.close()
