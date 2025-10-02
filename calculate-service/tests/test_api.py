from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SERVICE_ROOT.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from testing_utils.sync_client import create_client  # noqa: E402


def _load_module(module_name: str, relative_path: str):
    module_path = SERVICE_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(module_name, module)
    spec.loader.exec_module(module)
    return module


calculate_service_module = _load_module(
    "calculate_service_app", "app/__init__.py"
)
problem_bank_module = _load_module(
    "calculate_service_problem_bank", "app/problem_bank.py"
)
create_app = calculate_service_module.create_app
list_categories = problem_bank_module.list_categories


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture
def client(app):
    test_client = create_client(app)
    try:
        yield test_client
    finally:
        test_client.close()


def test_health_endpoint_returns_status(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "version" in payload
    assert "details" in payload
    assert "dependencies" in payload["details"]


def test_healthz_endpoint_reports_dependencies(client) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    dependencies = payload["details"]["dependencies"]
    assert dependencies["jinja2"]["status"] == "ok"


def test_readyz_endpoint_reports_readiness(client) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    readiness = payload["details"]["readiness"]
    assert readiness["templates"]["status"] == "ok"
    assert readiness["problem_bank"]["status"] == "ok"


def test_default_problem_category_is_returned(client) -> None:
    response = client.get("/api/problems")
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == list_categories()[0]
    assert body["total"] == len(body["items"])


def test_invalid_category_returns_problem_detail(client) -> None:
    response = client.get("/api/problems", params={"category": "INVALID"})
    assert response.status_code == 404
    body = response.json()
    assert body["type"].endswith("invalid-category")
    assert body["status"] == 404


def test_request_id_is_preserved(client) -> None:
    request_id = "test-request-id"
    response = client.get("/api/problems", headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_html_routes_emit_noindex_header(client) -> None:
    response = client.get("/problems")
    assert response.status_code == 200
    assert response.headers["X-Robots-Tag"] == "noindex"
