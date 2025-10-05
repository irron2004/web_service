# 360Me Senior Developer Brief

## 1. Product Snapshot
- **Mission**: Deliver the "If I were you" perception-gap experience, expanding to a multi-stage couple insight flow that compares self vs. partner perceptions and surfaces actionable coaching cards.
- **Users**: Korean-language couples (20–40s) and early adopters who invite peers; privacy guardrails enforce k≥3 anonymity before exposing shared aggregates.
- **Core Outcomes**: Session/invite flows, 32-question Likert survey, Δ calculations across 8 subscales, radar/scatter visualisations, OG share assets, and safety routing for high-risk signals.

## 2. Architecture Overview
```
[Client (Web/Mobile)]
    │
    ▼
[Cloudflare DNS + CDN + WAF]
    ├─► Cloudflare Pages (React/Vite build)
    └─► /api/* → Google Cloud Run (FastAPI container)
             ├─ Cloud SQL for PostgreSQL
             ├─ Redis (planned)
             └─ OpenTelemetry exporters → GCP Trace/Logging
```
- **Backend service (`mbti-arcade`)**: FastAPI + SQLAlchemy, core questionnaire, session, scoring, and aggregate APIs.
- **Supporting services**: `main-service` (landing/marketing FastAPI), 외부 저장소 [`calculate_math`](https://github.com/irron2004/calculate_math) (학습용 FastAPI+React) 등 실험 스택.
- **Observability & Compliance**: RFC 9457 error payloads, `X-Request-ID` propagation, OpenTelemetry spans, WCAG 2.2 AA, Web Vitals (LCP≤2.5s / INP≤200ms / CLS≤0.1), AdSense confirmed-click safeguards.

## 3. Technology Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2, Alembic migrations, Uvicorn ASGI.
- **Frontend**: React + TypeScript + Vite (planned rollout), Chart.js for radar/scatter, Jinja templates for legacy flows.
- **Data/Infra**: PostgreSQL (Cloud SQL), Redis/Memorystore (future cache), Cloudflare Pages for static deploy, Cloud Run for API containers, GitHub Actions CI/CD.
- **Testing & Quality**: Pytest (unit/integration/E2E), Lighthouse CI, axe accessibility checks, k6 performance, custom monitors mapped to metrics M-107..M-109.

## 4. Working Directory Highlights
```
web_service_new/
├─ mbti-arcade/           # Production backend (FastAPI app, models, data loaders, tests)
├─ main-service/          # Landing hub FastAPI service
├─ calculate_math/        # Ignored checkout of standalone FastAPI + React 학습 서비스
├─ docs/                  # Playbooks, testing guide, style guides, this brief
├─ mbti-arcade/docs/DeploymentPlan.md      # Cloudflare Pages + Cloud Run rollout playbook
├─ mbti-arcade/docs/PRD.md                 # Couple insight product requirements
├─ mbti-arcade/docs/DesignOptions.md       # Tech trade-off decisions (charts, OG images, aggregation)
├─ mbti-arcade/docs/product/Tasks.md   # Kanban with acceptance criteria & monitoring IDs
└─ mbti-arcade/docs/product/couple.md # Couple-specific TODO backlog
```
- `mbti-arcade/app/` houses FastAPI routers, domain services, SQLAlchemy models, and data seeds under `app/data/`.
- `mbti-arcade/tests/` contains the primary pytest suites (E2E, integration, share flow legacy cases).
- Documentation under `docs/` includes testing, frontend/api style, agent runbook, and observability procedures.

## 5. Current Delivery Status
- **Requirements**: PRD v1.0 ([`PRD`](../mbti-arcade/docs/PRD.md)) defines 3-stage couple flow, Δ calculations, safety protocols, decision packet sealing, and KPI/test traceability.
- **Design Decisions**: Chart.js selected for visualisations; server-side Satori/Sharp recommended for OG images; aggregation to run in backend worker. ([`DesignOptions`](../mbti-arcade/docs/DesignOptions.md))
- **Deployment Readiness**: [`DeploymentPlan`](../mbti-arcade/docs/DeploymentPlan.md) v1.0 maps Cloudflare Pages + Cloud Run setup, CI/CD pipelines, WAF/rate-limit rules, and week-by-week rollout timeline.
- **Implementation Backlog** ([`Tasks`](../mbti-arcade/docs/product/Tasks.md) & [`Couple`](../mbti-arcade/docs/product/couple.md)):
  - Backend P0 work pending: health checks, RFC 9457 middleware, self/other schema validation, OTel instrumentation, search-index guarding, OG image API.
  - Couple flow gaps: idempotent response upserts, decision packet schema, k-threshold exposure, audit logging, E2E failure scenarios, UX flows for tokens and result visualisations.
  - Observability and alerts: KPI exporter wiring, Slack/email alerts for stage transitions and rate limits, weekly smoke test cadence.

## 6. Immediate Next Steps (Suggested)
1. Implement backend P0 tasks (BE-01..BE-06) and land corresponding pytest coverage.
2. Deliver W1 deployment proof-points: Cloud Run sample service, Cloudflare Pages domain binding, Cloud SQL connectivity.
3. Finalise couple session data contracts (decision packets, audit events) ahead of UI integration.
4. Instrument OTel tracing & Web Vitals dashboards; define alert thresholds for high-risk Δ flags.

## 7. Open Questions / Risks
- Redis/Memorystore adoption timing for session caching and job queues.
- Safety escalation content: confirm external counselling resources and localisation copy.
- Confirm rollout of confirmed-click safeguards alongside AdSense slot placement templates.
- Coordination plan for blue/green rollbacks when schema migrations are involved (forward-fix vs. dual writes).

## 8. Reference Docs
- `README.md` – high-level product vision and repository map.
- [`Tasks`](../mbti-arcade/docs/product/Tasks.md) – sprint/Kanban with acceptance tests & monitoring IDs.
- `PRD.md` – couple insight requirements, metrics, and traceability.
- [`DeploymentPlan`](../mbti-arcade/docs/DeploymentPlan.md) – environment setup, CI/CD, rollout checklist.
- [`DesignOptions`](../mbti-arcade/docs/DesignOptions.md) – architecture trade-offs for charts, OG images, aggregation.
- `docs/testing.md` – verification matrix across QA, performance, and observability.
