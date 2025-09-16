**요약**
“한 작업=한 PR/커밋(≤200줄)” 원칙으로 BE/FE/품질/그로스 칸반을 구성했다. 각 항목은 **ID/요약/우선순위/의존성/수락 기준/테스트/모니터링(M-###)**를 포함한다.

```yaml
version: "0.9.0"
date: "2025-09-16"
domains: [backend, react, qa, growth]
owner: "PM"
source_of_truth: ["PRD.md"]
```

### 칸반(☐ TODO | ☐ WIP | ☐ REVIEW | ☐ DONE)

#### 백엔드

1. **BE-101** 스캐폴드/헬스체크/RFC 9457 미들웨어 — **P0**

   * 수락: `/healthz`,`/readyz` 200, 4xx/5xx **Problem Details** 출력
   * 테스트: 단위(스키마 스냅샷), 통합(오류 케이스) — **M-113** ([RFC Editor][1])
2. **BE-102** 질문/세션/응답 스키마 & CRUD — **P0**

   * 수락: 검증오류→9457, 트랜잭션 일관성
   * 테스트: Pydantic/DB 통합 — **M-102**
3. **BE-103** 채점/집계 엔진(가중치/σ/GapScore) — **P0**

   * 수락: 샘플 케이스 결과 일치, 경계값(모두 3/모두 5/혼합) 통과
   * 테스트: 속성 기반/경계값 — **M-105**
4. **BE-104** 레이트리밋(429/Retry-After) — **P1**

   * 수락: IP/토큰 한도, 재시도 헤더 포함 — **M-114** ([IETF Datatracker][5])
5. **BE-105** OTel & X-Request-ID — **P0**

   * 수락: 트레이스-로그 조인 — **M-112** ([opentelemetry-python-contrib.readthedocs.io][2])
6. **BE-106** OG 이미지 API(@vercel/og 또는 캡처) — **P1**

   * 수락: 200 PNG, P95<800ms — **M-108** ([Vercel][13])

#### 프론트엔드

1. **FE-101** Vite/Router/에러바운더리 — **P0**
2. **FE-102** Self 설문(24+8) UI/검증 — **P0**
3. **FE-103** 초대 링크 생성/상태 표시 — **P0**
4. **FE-104** 타인 응답 폼(익명/기명) — **P0**
5. **FE-105** 결과 레이더/스캐터 구현 — **P0** ([Chart.js][4])
6. **FE-106** OG 미리보기/공유(메타/noindex) — **P1** ([Google for Developers][12])
7. **FE-107** RUM(Web-Vitals) 스니펫 — **P0** ([web.dev][10])
8. **FE-108** 접근성(WCAG2.2 AA) — **P0** ([W3C][9])
9. **FE-109** AdSense 슬롯 템플릿(상/중/하) — **P1** ([Google Help][7])

#### 품질/보안/그로스

1. **Q-101** Lighthouse CI + RUM 파이프라인 — **P0** ([web.dev][10])
2. **Q-102** E2E 5시나리오(Playwright) — **P0**
3. **Q-103** ASVS v5.0 L2 드라이런 — **P0** ([OWASP Foundation][11])
4. **G-101** GA4 이벤트/UTM 템플릿 — **P0** ([Google Help][8])
5. **G-102** OG 카드 실험(A/B 텍스트) — **P1**

### NFR → 테스트/모니터링 매핑

| NFR          | 테스트/도구                    | 모니터링(M-###)           |
| ------------ | ------------------------- | --------------------- |
| LCP/INP/CLS  | Lighthouse CI(랩), RUM(필드) | **M-201** 웹바이탈        |
| P95<1s/에러<1% | k6/APM                    | **M-202** API 지연/에러   |
| RFC 9457 오류  | 스키마 스냅샷/계약                | **M-113** 오류 응답율      |
| ASVS v5 L2   | 체크리스트/DAST                | **M-203** 취약점 카운트     |
| AdSense 정책   | 수동 검수 체크                  | **M-110** Invalid CTR |

### 버퍼/롤백

* 버퍼 20%(채점/집계/차트 리스크).
* 롤백: Blue-Green, 마이그는 forward-fix + 백업 스냅샷.

[1]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html?utm_source=chatgpt.com "OpenTelemetry FastAPI Instrumentation"
[4]: https://www.chartjs.org/docs/latest/charts/radar.html?utm_source=chatgpt.com "Radar Chart"
[5]: https://datatracker.ietf.org/doc/html/rfc6585?utm_source=chatgpt.com "RFC 6585 - Additional HTTP Status Codes"
[7]: https://support.google.com/adsense/answer/1346295?hl=en&utm_source=chatgpt.com "Ad placement policies - Google AdSense Help"
[8]: https://support.google.com/analytics/answer/13316687?hl=en&utm_source=chatgpt.com "[GA4] Event naming rules - Analytics Help"
[9]: https://www.w3.org/TR/WCAG22/?utm_source=chatgpt.com "Web Content Accessibility Guidelines (WCAG) 2.2"
[10]: https://web.dev/articles/vitals?utm_source=chatgpt.com "Web Vitals | Articles"
[11]: https://owasp.org/www-project-application-security-verification-standard/?utm_source=chatgpt.com "OWASP Application Security Verification Standard (ASVS)"
[12]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag?utm_source=chatgpt.com "Robots Meta Tags Specifications | Google Search Central"
[13]: https://vercel.com/docs/og-image-generation?utm_source=chatgpt.com "Open Graph (OG) Image Generation"
