# Repository Guidelines

## Project Structure & Module Organization
- Core MBTI arcade service lives in `mbti-arcade/app/` (FastAPI, SQLAlchemy, Jinja templates). Supporting data and migrations sit under `mbti-arcade/app/data/` and `mbti-arcade/alembic/`.
- 학습용 계산 서비스는 별도 저장소 [`calculate_math`](https://github.com/irron2004/calculate_math)에 유지하며, 로컬에서는 `calculate_math/` 디렉터리로 체크아웃합니다.
- Shared templates and lightweight API examples reside in `main-service/app/templates/`. Documentation lives under `mbti-arcade/docs/` (product specs, deployment plan, tasks) and root-level `docs/` (shared playbooks). Deployment assets (Docker, nginx) stay at the repository root.

## Build, Test, and Development Commands
- `cd mbti-arcade && make setup` — create virtualenv and install Python dependencies.
- `make run` (inside `mbti-arcade/`) — launch `uvicorn app.main:app --reload --port 8000` for local iteration.
- `make check` — run Black, isort, flake8, pylint, and the pytest suite in one pass.
- `docker-compose up` — bring up the multi-service stack defined at the repo root for integration checks.

## Coding Style & Naming Conventions
- Python: Black (4 spaces, 88-char lines), isort, flake8, pylint. Use `snake_case` for functions, `CamelCase` for Pydantic models, and `PascalCase` for SQLAlchemy models.
- Templates: keep Jinja blocks compact; align with styles in `docs/frontend_style.md`.
- Configuration and secrets live in `.env` files ignored by git—never hardcode credentials.

## Testing Guidelines
- Primary tests are in `mbti-arcade/tests/` with legacy cases in `mbti-arcade/test_mbti.py`. FastAPI flows rely on pytest and httpx clients.
- Run `pytest` (or `make test`) before each PR; use markers (`@pytest.mark.slow`) so CI can filter heavy suites.
- Add unit coverage for scoring helpers, integration tests for repositories, and end-to-end flows for Self→Invite→Aggregate and couple sessions.

## Commit & Pull Request Guidelines
- Follow the existing history: imperative subjects ≤72 chars, optional Conventional prefixes like `feat(core): ...` and reference IDs from `docs/product/Tasks.md` when relevant.
- PRs should describe behavior changes, link specs (`docs/PRD.md`, `docs/DeploymentPlan.md`), list local test commands, and include screenshots or JSON samples for API/UI updates.
- Expect reviewers to block on missing RFC 9457 payloads, absence of k≥3 safeguards, or missing observability hooks.

## Security & Observability
- Every endpoint must propagate `X-Request-ID`, emit OpenTelemetry spans, and honor k-anonymity before exposing aggregates.
- Ensure share/result pages send `X-Robots-Tag: noindex` and scrub secrets from client bundles.
- Update `docs/DeploymentPlan.md` whenever Cloud Run or Cloudflare configs change to keep rollout checklists current.
