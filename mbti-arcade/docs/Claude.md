**요약(3–5줄)**
작게 배포·테스트 동반·표준 우선을 기본으로 하고, **RFC 9457/WCAG 2.2/Web Vitals** 준수와 **요청ID/OTel** 관측성을 강제합니다. 이번 사이클에서는 **k≥3 익명 임계**, **AdSense 의도치 클릭 방지**, **noindex/X-Robots-Tag** 적용을 Rule-Growing으로 승격했습니다.

```yaml
---
version: "1.0"
date: "2025-09-17"
owner: "PM: 이지율"
domains: ["process", "qa", "security"]
source_of_truth: "Claude.md"
use_browsing: true
---
```

### Golden Rules

1. PR≤300줄, 기능 플래그·롤백 준비.
2. 기능=테스트, 버그=회귀 테스트.
3. **오류=RFC 9457 / 접근성=WCAG 2.2 / 성능=Web Vitals**. ([RFC Editor][1])
4. **k≥3** 미만 결과 비공개(카드·공유 비활성). ([EPIC][2])
5. **AdSense 레이아웃**: 버튼/내비/드롭다운 근접 금지. ([Google Help][3])
6. 요청-트레이스-로그 **X-Request-ID/OTel** 상호탐색. ([opentelemetry-python-contrib][4])

### Rule-Growing(이번 사이클)

* **R-G-01** 결과/공유 URL **noindex/X-Robots-Tag** 강제. ([Google for Developers][5])
* **R-G-02** MBTI 상표 고지 & 공식 문항·타이포그래피 미사용. ([mbtionline.com][6])

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://epic.org/wp-content/uploads/privacy/reidentification/Sweeney_Article.pdf "k-ANONYMITY: A MODEL FOR PROTECTING PRIVACY"  
[3]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[4]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[5]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"  
[6]: https://www.mbtionline.com/en-US/Legal "Legal"
