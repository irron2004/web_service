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
    "calculate_service_app_pages_test", "app/__init__.py"
)
create_app = calculate_service_module.create_app
pages_module = calculate_service_module.pages


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


def test_problems_page_without_categories_shows_invite_notice(client, monkeypatch):
    monkeypatch.setattr(pages_module, "resolve_allowed_categories", lambda: [])
    response = client.get("/problems")
    assert response.status_code == 200
    body = response.text
    assert 'data-category-available="false"' in body
    assert "활성화된 문제 유형이 없습니다" in body
    assert "초대 링크를 생성할 수 없습니다" in body
