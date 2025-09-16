**요약(3–5줄)**
REST 스타일 가이드, DTO(Pydantic v2), **RFC 9457 오류 JSON**, **요청ID 규칙**, **버전 전략**, **레이트리밋/멱등성**을 명문화합니다. FastAPI 환경에서 **OpenTelemetry**와 함께 일관된 오류/로그 상관을 보장합니다. ([RFC Editor][1])

```yaml
---
version: "1.0"
date: "2025-09-16"
domains: ["backend"]
owner: "이지율"
source_of_truth: "docs/api_style.md"
use_browsing: true
---
```

### 엔드포인트 원칙

* 자원형 URI: `/sessions`, `/sessions/{id}`
* 버전: `Accept: application/vnd.360me.v1+json` 또는 `/v1/...`

### 스키마/검증

* **Pydantic v2** DTO, 입력 검증 실패는 400 Problem Details.

### 오류 응답(표준)

```json
{
  "type": "https://api.360me.app/errors/validation",
  "title": "Validation Failed",
  "status": 400,
  "detail": "field `title` is required",
  "instance": "/v1/sessions/...",
  "errors": { "title": ["required"] }
}
```

— **RFC 9457 Problem Details**(RFC 7807 대체). ([RFC Editor][1])

### 요청ID/로그 상관

* 수신된 `X-Request-ID` 사용, 없으면 발급→응답 헤더 반영, 전 구간 전파(미들웨어/컨텍스트). ([Starlette Context][18])

### 보안·레이트리밋/멱등성

* 인증: OIDC + JWT(iss/aud/exp 검증). ([OpenID Foundation][15])
* 레이트리밋 429(+`Retry-After`), POST 멱등 재시도 보호 `Idempotency-Key`.

---
