**요약(3–5줄)**
테스트 피라미드(Unit/Integration/E2E)에 채점·집계 수식 검증, 시각화 렌더링, 광고 배치 정책 검증을 포함했습니다. 성능은 **Web Vitals**, 접근성은 **WCAG 2.2**, 관측은 **OpenTelemetry**로 검증하며, RFC 9457 오류 스냅샷과 noindex 적용도 체크리스트에 포함합니다.

```yaml
---
version: "1.0"
date: "2025-09-17"
owner: "QA 리드"
domains: ["qa"]
source_of_truth: "docs/testing.md"
use_browsing: true
---
```

### 전략

* **Unit:** 정규화/가중치/σ/Gap 공식, RFC 9457 스키마 검증. ([RFC Editor][1])
* **Integration:** DB/Redis/메일 모의, OG 이미지 API 200ms SLA.
  * 헬스 프로브: `pytest mbti-arcade/tests/test_health.py -q`로 스냅샷을 남기고, `docker compose logs mbti-arcade | grep readyz`로 스타트업 타임스탬프를 확인합니다.
  * 참가자 플로우 계약: `pytest mbti-arcade/tests/integration/test_participant_flow.py -q`로 Self→Invite→Other→Preview 흐름을 검증하고 RFC 9457 스냅샷을 캡처합니다. (참고: docs/mbti_relationship_flow.md)
* **E2E:** Self→초대→응답→집계→차트→OG 공유.
* **성능:** Lighthouse CI + RUM/CrUX, LCP/INP/CLS 75p 합격. ([web.dev][2])
* **A11y:** WCAG 2.2 AA, 키보드 포커스·명도 대비. ([W3C][3])
* **광고:** 버튼/내비 거리, Confirmed-Click 모니터. ([Google Help][4])
* **관측:** OTel 스팬/로그/요청ID 상호 조인. ([opentelemetry-python-contrib][5])

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://web.dev/articles/vitals "Web Vitals | Articles"  
[3]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines (WCAG) 2.2"  
[4]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[5]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"
