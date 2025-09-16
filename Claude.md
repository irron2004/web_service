**요약**
작게 배포·테스트 동반·표준 우선. 이번 사이클 **Rule-Growing**에 ‘n<3 비공개’, ‘Ad 근접 배치 금지’, ‘GA4 이벤트 네이밍 규칙’, ‘429/Retry-After’ 등을 추가했다.

```yaml
version: "0.9.0"
date: "2025-09-16"
domains: [process, qa, security]
owner: "Tech Lead"
source_of_truth: ["PRD.md", "Tasks.md"]
```

### Golden Rules

1. **작게 배포**(PR≤200줄), 기능 플래그·롤백.
2. **테스트 동반**: 기능=테스트, 버그=회귀 테스트.
3. **표준 우선**: RFC 9457 오류, WCAG 2.2, **Web Vitals(INP)**. ([RFC Editor][1])
4. **데이터 보호**: 친구 **n<3 비공개**(연인은 1:1 예외).
5. **관측성 선행**: OTel/FastAPI 자동계측 + **X-Request-ID**. ([opentelemetry-python-contrib.readthedocs.io][2])

### 웹/API 규칙

* **요청ID**: 수신/미수신 시 발급, 전구간 전파.
* **오류 JSON**: RFC 9457 스키마 고정. ([RFC Editor][1])
* **레이트리밋**: 429/Retry-After, 정책 문서화. ([IETF Datatracker][5])
* **보안 헤더**: HSTS, CSP, Referrer-Policy.
* **noindex**: 결과/공유 페이지에 권장. ([Google for Developers][12])

### Growth/Ads 규칙

* AdSense **유도/근접 클릭 금지**(버튼/공유 옆 X), 2~3 슬롯 상한. ([Google Help][7])
* GA4 이벤트 네이밍: **소문자+언더스코어, 예약 접두어 금지**. ([Google Help][8])

### Rule-Growing(이번 사이클)

* **R-G-01**: 친구 집계 n<3 비공개(역추적 방지).
* **R-G-02**: 429 응답 시 **Retry-After** 포함. ([IETF Datatracker][5])
* **R-G-03**: OG 이미지에 PII 미표시, **noindex** 병행. ([Google for Developers][12])
* **R-G-04**: Ad 슬롯과 상호작용 요소 간 **간격 확보**(실수 클릭 방지). ([Google Help][7])
* **R-G-05**: INP 중심 최적화 전환(속성 기반 측정). ([web.dev][16])
* **R-G-06**: MBTI 상표 고지(공식 문항 불사용). ([mbtionline.com][3])

[1]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html?utm_source=chatgpt.com "OpenTelemetry FastAPI Instrumentation"
[3]: https://www.mbtionline.com/en-US/Legal?utm_source=chatgpt.com "Legal"
[5]: https://datatracker.ietf.org/doc/html/rfc6585?utm_source=chatgpt.com "RFC 6585 - Additional HTTP Status Codes"
[7]: https://support.google.com/adsense/answer/1346295?hl=en&utm_source=chatgpt.com "Ad placement policies - Google AdSense Help"
[8]: https://support.google.com/analytics/answer/13316687?hl=en&utm_source=chatgpt.com "[GA4] Event naming rules - Analytics Help"
[12]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag?utm_source=chatgpt.com "Robots Meta Tags Specifications | Google Search Central"
[16]: https://web.dev/blog/inp-cwv-launch?utm_source=chatgpt.com "Interaction to Next Paint is officially a Core Web Vital 🚀 | Blog"
