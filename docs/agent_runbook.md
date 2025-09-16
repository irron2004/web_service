**요약**
드라이런→승인→적용→관측→롤백 순으로 운영한다. 로그는 **X-Request-ID**로 보존(30일, PII 마스킹). **AdSense 정책/GA4 규칙** 위반 모니터링을 배치한다. ([opentelemetry-python-contrib.readthedocs.io][2])

```yaml
version: "0.9.0"
date: "2025-09-16"
domains: [ops]
owner: "Ops Lead"
source_of_truth: ["PRD.md", "Tasks.md"]
```

### 수칙

1. 변경 범위/위험 정리(ASK 게이트 항목 포함).
2. **드라이런**: 테스트 환경 데이터로 설문→집계→공유까지 재현.
3. **승인 기록**: 레이트리밋·Ad 슬롯·데이터 보존 변경은 승인 필수.
4. **실행**: 배포 후 OTel/웹바이탈/에러율 모니터.
5. **로그 보존**: 30일, PII 마스킹, 요청 추적은 X-Request-ID 사용. ([opentelemetry-python-contrib.readthedocs.io][2])
6. **롤백**: SLA 위반/LCP·INP 악화/Invalid CTR 급증 시 즉시 Blue-Green 전환. ([web.dev][10])

---

### 부록 A. 예시 API 오류(Problem Details)

```json
{
  "type": "https://api.360me.app/errors/validation",
  "title": "Validation Failed",
  "status": 400,
  "detail": "field `answers[3].value` must be 1..5",
  "instance": "/v1/self/submit",
  "errors": {"answers[3].value": ["range"]}
}
```

※ 표준: **RFC 9457**. ([RFC Editor][1])

### 부록 B. GA4 이벤트 네이밍(예시)

* `test_start`, `self_submit`, `invite_create`, `other_submit`, `result_view`, `share_click`
* 규칙: **영문/숫자/언더스코어, 소문자**, 예약 접두어·이름 금지. ([Google Help][8])

### 부록 C. AdSense 배치 가이드(초기)

* 위치: **제목 아래 1**, **차트 아래 1**, **하단 1**(최대 3).
* 금지: 버튼/링크/공유 근접 배치, 유도 문구/화살표/오해 유발 헤딩. ([Google Help][7])

[1]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html?utm_source=chatgpt.com "OpenTelemetry FastAPI Instrumentation"
[7]: https://support.google.com/adsense/answer/1346295?hl=en&utm_source=chatgpt.com "Ad placement policies - Google AdSense Help"
[8]: https://support.google.com/analytics/answer/13316687?hl=en&utm_source=chatgpt.com "[GA4] Event naming rules - Analytics Help"
[10]: https://web.dev/articles/vitals?utm_source=chatgpt.com "Web Vitals | Articles"
