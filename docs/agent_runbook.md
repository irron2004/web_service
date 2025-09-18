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

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[3]: https://web.dev/articles/vitals "Web Vitals | Articles"  
[4]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[5]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"
