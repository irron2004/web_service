# Repository Guidelines

## Project Structure & Module Organization
- Core MBTI arcade service lives in `mbti-arcade/app/` (FastAPI, SQLAlchemy, Jinja templates). Supporting data and migrations sit under `mbti-arcade/app/data/` and `mbti-arcade/alembic/`.
- The repo temporarily co-hosts the 360Me perception-gap stack (`mbti-arcade/`) and the
  standalone math API in `calculate-service/` so we can operate behind one domain; once
  the `calc.360me.app` pipeline is stable, plan on splitting calculate-service into its
  own repository and deployment track.
- Shared templates and lightweight API examples reside in `main-service/app/templates/`; `calculate-service/app/` is now a standalone FastAPI sample kept in sync as an external-facing service. Experimental math content is isolated in `math-app/` (frontend under `math-app/frontend/`, backend in `math-app/backend/`).
- Documentation and playbooks are under `docs/`, while deployment assets (Docker, nginx) are at the repository root.

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
- Follow the existing history: imperative subjects ≤72 chars, optional Conventional prefixes like `feat(core): ...` and reference IDs from `Tasks.md` when relevant.
- PRs should describe behavior changes, link specs (PRD, DeploymentPlan), list local test commands, and include screenshots or JSON samples for API/UI updates.
- Expect reviewers to block on missing RFC 9457 payloads, absence of k≥3 safeguards, or missing observability hooks.

## Security & Observability
- Every endpoint must propagate `X-Request-ID`, emit OpenTelemetry spans, and honor k-anonymity before exposing aggregates.
- Ensure share/result pages send `X-Robots-Tag: noindex` and scrub secrets from client bundles.
- Update `DeploymentPlan.md` whenever Cloud Run or Cloudflare configs change to keep rollout checklists current.
