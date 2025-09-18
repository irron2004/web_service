**요약(3–5줄)**
자원형 REST와 DTO(Pydantic v2), **RFC 9457 오류 JSON**, **요청ID 전파**, 버전 전략, 레이트리밋/멱등키 규칙을 정의합니다. 결과/공유 URL은 **noindex/X-Robots-Tag** 적용을 권장하며, 모든 4xx/5xx 응답은 RFC 9457 스키마를 따라야 합니다.

```yaml
---
version: "1.0"
date: "2025-09-17"
owner: "BE 리드"
domains: ["backend"]
source_of_truth: "docs/api_style.md"
use_browsing: true
---
```

### 엔드포인트 원칙

* 자원형 URI: `/sessions`, `/sessions/{id}`
* 버전 전략: `Accept: application/vnd.360me.v1+json` 또는 `/v1/...`

### 스키마/검증

* DTO는 Pydantic v2 사용, 검증 실패는 400 Problem Details.

### 오류 포맷

```json
{
  "type": "https://api.360me.app/errors/validation",
  "title": "Validation Failed",
  "status": 400,
  "detail": "field `title` is required",
  "instance": "/v1/sessions/...",
  "errors": {"title": ["required"]}
}
```

— **RFC 9457 Problem Details**(RFC 7807 대체). ([RFC Editor][1])

### 요청ID/로그 상관

* 수신된 `X-Request-ID` 사용, 없으면 발급 후 응답 헤더에 포함.
* 요청-로그-트레이스를 OTel 컨텍스트로 연동. ([opentelemetry-python-contrib][2])

### 보안·레이트리밋·멱등성

* 429 + `Retry-After`, POST 재시도 보호 `Idempotency-Key`.
* 결과/공유 URL은 `noindex` 메타 또는 `X-Robots-Tag` 헤더 적용. ([Google for Developers][3])

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[3]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"
