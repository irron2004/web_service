**요약(3–5줄)**
운영은 **Dry-run → 승인 → 단계별 배포 → 모니터링 → 롤백** 순서로 수행하며, 배포 전 **OTel 대시보드**와 **AdSense 정책 체크리스트**를 확인합니다. 결과/공유 페이지는 **noindex/X-Robots-Tag**로 보호하고, Confirmed-Click이나 정책 위반 발생 시 즉시 레이아웃 수정 또는 롤백합니다.

```yaml
---
version: "1.0"
date: "2025-09-17"
owner: "Ops 리드"
domains: ["ops"]
source_of_truth: "docs/agent_runbook.md"
use_browsing: true
---
```

### 배포 플로우

1. Scope 확인 및 Ask 게이트 검토.
2. **Dry-run**: Self→초대→응답→집계→OG 공유까지 재현.
3. 승인 기록(정책·변경 영향).
4. 단계적 배포 + 실시간 모니터링(Web Vitals, 에러율, Confirmed-Click).
5. **로그 보존 30일**, 요청 추적은 X-Request-ID 기반. ([opentelemetry-python-contrib][2])
6. SLA 악화·Confirmed-Click·정책 위반 발생 시 Blue-Green 롤백.

### 체크리스트

* [ ] 스테이징 **E2E 5시나리오** 통과
* [ ] Web Vitals(75p) 합격(랩/필드) ([web.dev][3])
* [ ] RFC 9457 오류 스냅샷 OK ([RFC Editor][1])
* [ ] OTel/요청ID 조인 확인 ([opentelemetry-python-contrib][2])
* [ ] AdSense **의도치 클릭 방지** 검수 ([Google Help][4])
* [ ] 결과/공유 URL `noindex`/`X-Robots-Tag` 적용 ([Google for Developers][5])
* [ ] 커플 리포트 PDF/JSON 템플릿 동기화 (`partner_report_template.yaml` 기준)

### 로그↔스팬 코릴레이션 절차

1. FastAPI 미들웨어가 모든 요청에 `X-Request-ID`를 부여하고, 동일 ID를 로깅 컨텍스트에 바인딩합니다.
2. `configure_observability`는 OTLP 엔드포인트·헤더·타임아웃을 환경변수로 읽어 OpenTelemetry 트레이서를 초기화하고, 로그 필터가 `request_id`, `trace_id`, `span_id`를 주입합니다.
3. 장애 발생 시 `trace_id`로 OTEL 대시보드에서 스팬을 조회한 뒤, 같은 로그 라인의 `request_id`를 이용해 API 게이트웨이·워크커 로그를 추적합니다.
4. 로그에 `trace_id`가 비어 있으면 OTLP 수집기 연결 상태를 확인하고, `X-Request-ID`만으로라도 장애 타임라인을 복원합니다.

### 커플 플로우 롤백 전략

1. **트랜잭션 단위** — `CoupleService`의 `create_session`, `update_stage_one`, `upsert_responses`, `compute_result`는 FastAPI 라우터에서 `service.db.commit()` 호출 전 예외가 발생하면 자동 `rollback()` 하도록 구성되어 있습니다. 오류 발생 시 `AuditEvent`에 `event_type=error.*`를 남기고 Slack 알림을 발송합니다.
2. **즉시 조치** — Stage3 결과 계산 실패 또는 `question-invalid` 오류 급증 시, 최근 성공 배포 이미지로 Cloud Run을 롤백하고 `decision_packets` 테이블을 검사하여 불완전한 행을 삭제합니다.
3. **데이터 검증** — 롤백 직후 `GET /api/couples/sessions/{id}`와 `GET /responses`로 k-state, 완료 플래그가 기대값(기본값 false, 응답 없음)인지 확인합니다.
4. **후속 작업** — PRD와 `partner_report_template.yaml`을 대조하여 규칙 변경이 필요한지 검토하고, 장애 보고서에 재현 절차·차단 방안을 기록합니다.

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[3]: https://web.dev/articles/vitals "Web Vitals | Articles"  
[4]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[5]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"
