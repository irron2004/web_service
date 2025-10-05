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

### 공유 OG 이미지 규격

* 응답 크기: 1200×630 PNG, 배경/배너는 사전 렌더된 템플릿을 복제해 200ms 이하(경고 임계 150ms)로 생성.
* 캐시 정책: `Cache-Control: public, max-age=600` + `ETag`(이미지 해시), 응답 헤더에 `X-Robots-Tag=noindex` 유지.
* 집계가 잠긴 상태(K<3)는 배너를 잠금 복사본으로 표시하며, 로그에는 렌더링 시간(ms), 세션ID, 모드, K를 기록한다.

---

### 결정 패킷 버전 관리

커플 플로우의 결과 산출물은 `decision_packets` 테이블에 저장되며 다음 원칙을 따른다.

1. **구조** — `payload.inputs`(참여자 응답, K 상태, stage 스냅샷)와 `payload.outputs`(스케일, 델타, 플래그, 인사이트, top_delta_items, gap_summary)를 JSON으로 보존한다.
2. **해시** — JSON을 정렬(`sort_keys=True`) 후 SHA-256으로 서명한 값이 `packet_sha256`이며, API 응답에서 무결성 확인용으로 제공된다.
3. **모델 버전** — `model_id`는 `core_scoring.v{n}` 형태로, 스코어링 로직이 변하면 반드시 증가시킨다. 구버전 호환이 필요하면 마이그레이션 스크립트 또는 변환 레이어를 제공한다.
4. **코드 참조** — `code_ref`는 빌드/커밋 SHA, CI 태그 등 배포 스냅샷을 넣어 추후 감사가 가능하도록 한다.
5. **API 응답** — `GET /api/couples/.../compute` 응답에는 `decision_packet.packet_sha256`, `code_ref`, `model_id`, `created_at`, `generated_at`가 포함되어야 하며, 변경 시 하위 호환성 공지를 `CHANGELOG`에 반영한다.

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[3]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"
