# Calculate Service Overview

## Endpoints

| Method | Path         | Description |
|--------|--------------|-------------|
| GET    | `/health`    | Returns overall service health information including the deployed version and dependency summaries. |
| GET    | `/healthz`   | Lightweight liveness probe that mirrors `/health` and is suitable for container orchestrator health checks. |
| GET    | `/readyz`    | Readiness probe that validates template loading and problem data availability before routing production traffic. |
| GET    | `/api/problems` | Fetches a list of practice problems for an optional category. |
| GET    | `/problems`  | Renders the HTML landing page for browsing practice problems. |

Each health response includes a `status` field for quick inspection and a `details` object that surfaces dependency and readiness diagnostics for observability tooling.
