# Repository Guidelines

## Project Structure & Module Organization
Core perception-gap logic lives in `mbti-arcade/app/` (FastAPI, SQLAlchemy, Jinja). Shared templates and assets sit in `main-service/app/templates/`, while auxiliary examples reside in `calculate-service/` and `math-app/`. Operational docs and style guides are under `docs/`, and deployment artifacts live alongside `docker-compose.yml` and `nginx/` sample configs. Treat `Tasks.md` and `DeploymentPlan.md` as the authoritative roadmap for scope and releases.

## Build, Test, and Development Commands
From `mbti-arcade/`, `make setup` provisions the virtualenv and dependencies, `make run` starts `uvicorn app.main:app --reload --port 8000`, and `make prod` spawns a four-worker server. `make test` (or `pytest tests/`) runs the perception-gap suite; `make check` chains formatting, lint, and tests. For lightweight services run `uvicorn app.main:app --reload --port 8080` inside `main-service/` and `calculate-service/`. Use the `docker-compose.yml` at the repo root when validating multi-service flows locally.

## Coding Style & Naming Conventions
Python modules follow Black formatting (4-space indent, 88-char lines), isort ordering, and flake8/pylint lint gates—prefer `snake_case` for functions, `CamelCase` for Pydantic models, and `PascalCase` SQLAlchemy models mapped in `app/models.py`. API responses must honor RFC 9457 Problem Details with deterministic `type` URLs. Frontend experiments stay consistent with `docs/frontend_style.md`: Vite + React Router, TanStack Query for server state, and WCAG 2.2 AA-friendly components.

## Testing Guidelines
Tests live in `mbti-arcade/tests/` plus legacy coverage in `test_mbti.py`. New contributions ship with unit coverage for scoring helpers, integration checks for repositories, and FastAPI E2E paths mirroring the Self→Invite→Aggregate flow. Prior to PRs, run `pytest -m "not slow"` if you add markers and capture coverage for gap formulas and anonymity enforcement. Refer to `docs/testing.md` for Web Vitals, WCAG, AdSense, and OpenTelemetry checkpoints.

## Commit & Pull Request Guidelines
Match the existing history: imperative subject lines, ≤72 chars, optional Conventional Commits prefixes (`feat(core):`, `fix`, `chore`). Reference task IDs from `Tasks.md` when applicable and note config migrations in the body. PRs should describe behaviour changes, link supporting docs (PRD, DeploymentPlan), list local test commands executed, and attach screenshots or JSON samples for API/UI tweaks. Expect reviewers to block on missing RFC 9457 payloads, k≥3 safeguards, or absent observability hooks.

## Security & Observability Checks
Every new endpoint must propagate `X-Request-ID`, emit OpenTelemetry spans, and maintain k-anonymity before exposing aggregates. Confirm `noindex` headers on share/result pages and avoid embedding secrets in client bundles. When touching Cloud Run or Cloudflare surfaces, update the corresponding section in `DeploymentPlan.md` so rollout checklists stay accurate.
