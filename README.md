# 360Me – Perception Gap Platform

360Me delivers the "If I were you" perception-gap experience. We compare how people see themselves versus how others see them, surface the gaps, and make it easy to share insights. This monorepo keeps the FastAPI backend, supporting services, and the product/operations docs together so experiments and deployments stay consistent.

- **Key specs**: `PRD.md`, `DesignOptions.md`, `Tasks.md`, `DeploymentPlan.md`, and the guides under `docs/`
- **Mandatory standards**: RFC 9457 error schema, WCAG 2.2 AA, Web Vitals (LCP≤2.5 s / INP≤200 ms / CLS≤0.1), OpenTelemetry observability, k≥3 anonymity safeguard, AdSense confirmed-click prevention

---

## 1. Product Vision & Planning

360Me is built as a staged roll-out:

- **Problem & audience** – Young adults share a self-test, invite partners/friends, and explore gap scores. Privacy is guarded with k-anonymity and noindex policies.
- **MVP scope** – 32-question Likert survey (24 common + 8 mode boosters), session/invite flow, radar & scatter visualisations, OG share cards. Roadmap and assumptions live in `PRD.md`.
- **Traceability** – `Tasks.md` links functional requirements (R-###) to tests (T-###) and metrics (M-###). Release acceptance focuses on full E2E runs, Web Vitals, RFC 9457 compliance, k≥3 enforcement, and AdSense policy checks.
- **Deployment strategy** – Documented in `DeploymentPlan.md`: FE on Cloudflare Pages, BE on Cloud Run (asia-northeast3), Cloud SQL (PostgreSQL), Cloudflare WAF/CDN, GitHub Actions CI/CD, canary via Cloud Run traffic splitting.

---

## 2. Engineering Highlights

| Area | Details |
|------|---------|
| Questionnaire & scoring | `docs/questionnaire.v1.json` seeds the 24+8+8 items; `app/data/questionnaire_loader.py` validates/normalises and assigns deterministic numeric IDs. Scoring follows the PRD formulas (normalisation, weighted σ, GapScore).
| API design | REST endpoints under `/api/*` use Pydantic v2 models, RFC 9457 error payloads, X-Request-ID propagation, and OpenTelemetry hooks. Session creation, self/other submissions, and aggregate retrieval stay within FastAPI.
| Persistence | SQLAlchemy models (`app/models.py`) cover users, sessions, questions, responses, aggregates. Seed logic keeps DB questions in sync with the JSON source. Aggregation enforces k-anonymity before exposing chart data.
| Frontend templates | Jinja templates (under `app/templates/mbti/`) render the self/other forms, friend/couple modes, and OG previews; Chart.js is the target for radar/scatter visualisations per `DesignOptions.md`.
| Observability & policy | Golden rules (defined in `Claude.md`) require OpenTelemetry, Web Vitals monitoring, WCAG 2.2 accessibility patterns, and AdSense "confirmed click" avoidance. `docs/testing.md` explains the verification matrix.

---

## 3. Repository Layout

```
web_service_new/
|- calculate-service/        # Auxiliary FastAPI example service
|- main-service/             # Hub/landing FastAPI app (Jinja templates)
|- math-app/                 # Simple learning SPA
|- mbti-arcade/              # Core perception-gap API (FastAPI + SQLAlchemy)
|- nginx/                    # Local reverse-proxy sample configs
|- docs/                     # Operational, testing, and style guides
|- DeploymentPlan.md         # Cloudflare Pages + Cloud Run deployment plan
|- PRD.md / DesignOptions.md / Tasks.md
|- README-Docker-Integrated.md (additional reference)
```

All services can run independently; `mbti-arcade` is the production backend for the perception-gap MVP.

---

## 4. Service Overview

| Service            | Tech stack           | Responsibilities |
|--------------------|----------------------|------------------|
| `mbti-arcade`      | FastAPI, SQLAlchemy, Jinja | Questionnaire API, session/invite flow, self & other submissions, aggregation, OG images |
| `main-service`     | FastAPI, Jinja       | Hub landing pages, links to other apps, health endpoints |
| `calculate-service`| FastAPI              | Education-themed sample API |
| `math-app`         | Static SPA (HTML/JS) | Lightweight teaching site |
| `nginx`            | Nginx configs        | Dev reverse-proxy examples |

### Deployment targets
- Frontend: Vite build → Cloudflare Pages (`app.360me.app` custom domain)
- Backend: Containerised FastAPI → Google Cloud Run (`asia-northeast3`), connected to Cloud SQL for PostgreSQL via Secret Manager credentials
- Edge: Cloudflare DNS/CDN/WAF with Cache Rules and Rate Limiting
- Full rollout details live in [`DeploymentPlan.md`](DeploymentPlan.md)

---

## 5. Local Development

### Common setup
```bash
git clone <repo-url>
cd web_service_new
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### Run the core API (`mbti-arcade`)
```bash
cd mbti-arcade
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Health check: `GET http://localhost:8000/health`
- Primary endpoints: `/api/sessions`, `/api/self/submit`, `/api/other/submit`, `/api/result/{token}` (errors return RFC 9457 JSON)

### Hub service (`main-service`)
```bash
cd ../main-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Sample calculator (`calculate-service`)
```bash
cd ../calculate-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

Need to proxy multiple services behind one origin? See the `nginx/` folder for example configs.

---

## 6. Quality & Testing

- `mbti-arcade/tests/` includes E2E and integration coverage. FastAPI 0.110 removed `APIRouter.exception_handler`; adjust the legacy tests (`test_mbti.py`, `tests/test_share_flow.py`) when upgrading old flows.
- `docs/testing.md` documents the test pyramid plus Web Vitals, WCAG, AdSense, and OpenTelemetry verification routines.
- Golden rules: every new capability ships with tests; any dataset with fewer than three raters stays private (no charts, no sharing).

---

## 7. Deployment Checklist (Condensed)

1. Frontend: create a Cloudflare Pages project, run `npm run build`, publish the `dist/` folder, map `app.360me.app`.
2. Backend: build & push a container to Artifact Registry, deploy to Cloud Run (`asia-northeast3`), confirm `/health`.
3. Database & secrets: provision Cloud SQL (PostgreSQL), store the DSN in Secret Manager, grant the Cloud Run service account.
4. Routing: point `api.360me.app` at the Cloud Run HTTPS endpoint, enable Cloudflare WAF and rate limiting for critical POST routes.
5. CI/CD: add GitHub Actions workflows for Pages and Cloud Run deployments; configure secrets (`CF_API_TOKEN`, `CF_ACCOUNT_ID`, `GCP_PROJECT`, `GCP_SA_KEY`, `GAR_HOST`).
6. Observability: wire OpenTelemetry tracing/logging, build dashboards for release P95, error rate, and Web Vitals.
7. Policy checks: publish `ads.txt`, enforce `noindex`/`X-Robots-Tag` on result/share endpoints, verify RFC 9457 + WCAG 2.2 compliance.

---

## 8. Documentation Index

| File | Purpose |
|------|---------|
| `PRD.md` | Product requirements, KPIs, traceability matrix |
| `DesignOptions.md` | Radar/Scatter chart, OG image, aggregation trade-offs |
| `Tasks.md` | Kanban board with acceptance criteria and metric mapping |
| `DeploymentPlan.md` | Cloudflare Pages + Cloud Run rollout plan and checklists |
| `docs/api_style.md` | REST patterns, RFC 9457 example payloads |
| `docs/frontend_style.md` | React Router, TanStack Query, Zustand, Chart.js guidance |
| `docs/testing.md` | Testing, performance, accessibility, observability strategy |
| `docs/agent_runbook.md` | Operations, release, rollback procedures |
| `CLOUDFLARE-SETUP.md` | Cloudflare Pages/Workers setup notes |

---

## 9. Contributing & Licence

1. Fork the repo → create `feature/<topic>` → commit → open a PR.
2. Ensure new work follows the golden rules (tests, rollout plan, k-anonymity, AdSense safety, etc.).
3. Licence: MIT.

For questions or bug reports, open an issue. Enjoy building better self/peer insight tools!
