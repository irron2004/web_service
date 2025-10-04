from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SERVICE_ROOT.parent

if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from testing_utils.sync_client import create_client  # noqa: E402


# NOTE: Telemetry exporters are validated in integration smoke tests. These
# tests focus on ensuring middleware behaviour remains backwards compatible.

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
reset_problem_cache = problem_bank_module.reset_cache
get_settings = config_module.get_settings
AttemptRepository = repositories_module.AttemptRepository


@pytest.fixture
def dataset(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    problems_path = data_dir / "problems.json"
    attempts_path = data_dir / "attempts.db"
    sample_problems = [
        {
            "id": "sample-add-1",
            "category": "덧셈",
            "question": "10 + 5 = ?",
            "answer": 15,
        },
        {
            "id": "sample-sub-1",
            "category": "뺄셈",
            "question": "10 - 3 = ?",
            "answer": 7,
        },
        {
            "id": "sample-add-2",
            "category": "덧셈",
            "question": "20 + 10 = ?",
            "answer": 30,
        },
    ]
    problems_path.write_text(
        json.dumps(sample_problems, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    monkeypatch.setenv("PROBLEM_DATA_PATH", str(problems_path))
    monkeypatch.setenv("ATTEMPTS_DATABASE_PATH", str(attempts_path))

    get_settings.cache_clear()  # type: ignore[attr-defined]
    reset_problem_cache()

    try:
        yield {
            "problems_path": problems_path,
            "attempts_path": attempts_path,
            "problems": sample_problems,
        }
    finally:
        reset_problem_cache()
        get_settings.cache_clear()  # type: ignore[attr-defined]


@pytest.fixture
def app(dataset):
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
    """RequestContextMiddleware should echo back caller provided IDs."""

    request_id = "test-request-id"
    response = client.get("/api/problems", headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_html_routes_emit_noindex_header(client) -> None:
    response = client.get("/problems")
    assert response.status_code == 200
    assert response.headers["X-Robots-Tag"] == "noindex"


def test_submit_correct_attempt_records_success(client, dataset) -> None:
    target = dataset["problems"][0]
    assert str(client._app.state.problem_repository.source_path) == str(
        dataset["problems_path"]
    )
    response = client.post(
        f"/api/problems/{target['id']}/attempts",
        json={"answer": target["answer"]},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["is_correct"] is True
    assert payload["correct_answer"] == target["answer"]
    assert payload["submitted_answer"] == target["answer"]

    repository = AttemptRepository(dataset["attempts_path"])
    attempts = repository.list_attempts(target["id"])
    assert len(attempts) == 1
    assert attempts[0].is_correct is True
    assert attempts[0].submitted_answer == target["answer"]


def test_submit_incorrect_attempt_is_logged(client, dataset) -> None:
    target = dataset["problems"][1]
    assert str(client._app.state.problem_repository.source_path) == str(
        dataset["problems_path"]
    )
    wrong_answer = target["answer"] + 5
    response = client.post(
        f"/api/problems/{target['id']}/attempts",
        json={"answer": wrong_answer},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["is_correct"] is False
    assert payload["correct_answer"] == target["answer"]
    assert payload["submitted_answer"] == wrong_answer

    repository = AttemptRepository(dataset["attempts_path"])
    attempts = repository.list_attempts(target["id"])
    assert len(attempts) == 1
    assert attempts[0].is_correct is False
    assert attempts[0].submitted_answer == wrong_answer


def test_submit_attempt_without_answer_returns_validation_error(client, dataset) -> None:
    target = dataset["problems"][2]
    response = client.post(
        f"/api/problems/{target['id']}/attempts",
        json={},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["detail"][0]["loc"][-1] == "answer"
