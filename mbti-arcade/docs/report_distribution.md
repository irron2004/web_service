# Couple Report Distribution Notes

## Inputs
- Produced from `CoupleResultEnvelope` (see `app/couple/schemas.py`).
- Mapping highlights:
  - `scales`, `deltas`, `flags`, `insights`, `top_delta_items`, `gap_summary` feed the narrative sections.
  - `k_state.current|threshold|visible` drives status badges.
  - `decision_packet.packet_sha256`, `code_ref`, `model_id`, `created_at` are embedded in the footer for audit.

## Pipeline
1. After `POST /api/couples/sessions/{id}/compute`, the backend emits a `CoupleResultEnvelope` JSON.
2. Render service consumes the envelope and hydrates `docs/partner_report_template.yaml` variables (names, percentages, axis shift).
3. Output targets:
   - **JSON**: raw envelope plus `report_version` stored in S3/Cloud Storage (signed URL valid for 24h).
   - **PDF**: Jinja template → WeasyPrint → stored alongside JSON with identical `packet_sha256` filename.
4. Delivery: `/api/couples/sessions/{id}/report` issues pre-signed URLs (auth-restricted) and logs an `AuditEvent` (`event_type="report.generated"`).
- **Audit fields** — `session_id`, `req_id`, `event_type`, payload에 `code_ref`, `model_id`, `packet_sha256`, `k_state` 요약을 포함해 사후 분석을 지원합니다.

## Versioning
- `model_id` and `code_ref` travel with JSON/PDF to support diffing.
- Increment `model_id` (e.g., `core_scoring.v2`) when scoring/flag logic changes.
- Maintain changelog entries detailing report schema adjustments.
