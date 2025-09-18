**요약(3–5줄)**
백엔드/프런트/품질 작업을 한 PR/커밋(≤200줄) 단위로 쪼개고, 각 항목에 **수락 기준·테스트·모니터링(M-###)**를 연결했습니다. Ask 게이트(공개 API, 스키마, 의존성, 보안, 대규모 수정)는 제안만 허용합니다. 전체 작업은 Web Vitals·RFC 9457·OTel·AdSense 정책 준수 흐름에 맞춰 구성했습니다.

```yaml
---
version: "1.0"
date: "2025-09-17"
owner: "PM: 이지율"
domains: ["backend", "frontend", "qa", "growth"]
source_of_truth: "Tasks.md"
use_browsing: true
---
```

### 칸반 (☐ TODO｜☐ WIP｜☐ REVIEW｜☐ DONE)

#### 백엔드

1. **BE-01** 스캐폴드/헬스체크(`/healthz`,`/readyz`) — **P0**  
   *수락:* 200 응답, 컨테이너 부팅≤30s. *모니터링:* M-107/M-108.
2. **BE-02** RFC 9457 오류 미들웨어 — **P0** *(Ask: 전역 미들웨어 도입)*  
   *수락:* 모든 4xx/5xx 스냅샷 매칭. ([RFC Editor][1])
3. **BE-03** Self/Other 스키마·검증·트랜잭션 — **P0**  
   *수락:* CRUD OK, 검증 실패는 RFC 9457.
4. **BE-04** 집계/Gap 워커 — **P1**  
   *수락:* 공식 일치, 단위테스트 100% 경계값.
5. **BE-05** OTel + X-Request-ID — **P0**  
   *수락:* 요청-스팬-로그 조인 가능. ([opentelemetry-python-contrib][2])
6. **BE-06** `X-Robots-Tag`/`noindex` 헤더/메타 — **P0**  
   *수락:* 결과/공유 URL 검색 제외. ([Google for Developers][3])
7. **BE-07** OG 이미지 API(`/share/og/{token}.png`) — **P1**  
   *수락:* 1200×630, <200ms, 캐시 헤더. ([ogp.me][4])

#### 프런트엔드

1. **FE-01** 라우팅/에러바운더리/스켈레톤 — **P0**
2. **FE-02** Self 폼(32문항) + 진행바 — **P0**
3. **FE-03** 초대 생성/공유 링크 — **P0**
4. **FE-04** Other 응답 폼(토큰/중복 방지) — **P0**
5. **FE-05** 레이더/스캐터(Chart.js) — **P1** ([chartjs.org][5])
6. **FE-06** GA4 이벤트/UTM — **P0** ([Google Analytics][6])
7. **FE-07** AdSense 안전 슬롯 템플릿 — **P0** ([Google Help][7])

#### 품질/보안

1. **Q-01** Lighthouse(RUM/CrUX 연동) 파이프라인 — **P0** ([web.dev][8])
2. **Q-02** A11y(axe 자동/수동) — **P0** ([W3C][9])
3. **Q-03** 광고 정책 체커(근접 요소 경고) — **P1** ([Google Help][7])

### NFR → 테스트/모니터링 매핑

| NFR            | 테스트/도구                    | 모니터링 |
| -------------- | ----------------------------- | -------- |
| Web Vitals(75p)| Lighthouse CI, RUM/CrUX       | **M-107** |
| RFC 9457       | 스냅샷/계약 테스트             | **M-108** |
| Confirmed-Click| 레이아웃 룰·정책 모니터링      | **M-109** |

### 버퍼/롤백

* 버퍼 20%(채점/집계/차트 리스크).
* Blue-Green, 데이터 변경은 forward-fix(+스냅샷).

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[3]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"  
[4]: https://ogp.me/ "The Open Graph protocol"  
[5]: https://www.chartjs.org/docs/latest/charts/radar.html "Radar Chart"  
[6]: https://developers.google.com/analytics/devguides/collection/ga4/reference/events "Recommended events | Google Analytics"  
[7]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[8]: https://web.dev/articles/vitals "Web Vitals | Articles"  
[9]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines (WCAG) 2.2"
