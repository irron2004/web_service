**요약**
테스트 피라미드(Unit/Integration/E2E)와 **채점/집계의 수학적 정합성** 테스트를 명시한다. Web Vitals(특히 **INP**)와 접근성(WCAG 2.2 AA) 자동/수동 점검을 병행한다. ([web.dev][16])

```yaml
version: "0.9.0"
date: "2025-09-16"
domains: [qa]
owner: "QA Lead"
source_of_truth: ["PRD.md", "Tasks.md"]
```

### 계층/전략

* **Unit**: 채점(norm), 표준편차(σ), GapScore 경계값(모두 3 → 0점/0σ, 모두 5 → 극단값)
* **Integration**: DB 트랜잭션/중복 제출/레이트리밋 429/Retry-After 동작. ([IETF Datatracker][5])
* **E2E(Playwright)**: ① Self 완료 ② 초대 발급 ③ 3인 응답 ④ 결과/공유 ⑤ 필터/히스토리.
* **A11y**: 키보드 완전 탐색/명도 대비 4.5:1, 스크린리더 레이블. ([W3C][9])
* **Perf/Vitals**: Lighthouse CI(랩), RUM 필드에서 LCP/INP/CLS 75p 합격. ([web.dev][10])

### 명명/픽스처

* 테스트명: `scoring_norm_spec.py`, `aggregation_gap_spec.py`, `result_chart.test.tsx`
* 고정 데이터: 샘플 응답 시퀀스(경계/무작위/병합 케이스)

### 커버리지

* **라인 80%+**, 핵심(채점/집계/시각화 데이터) **90%+**.

[5]: https://datatracker.ietf.org/doc/html/rfc6585?utm_source=chatgpt.com "RFC 6585 - Additional HTTP Status Codes"
[9]: https://www.w3.org/TR/WCAG22/?utm_source=chatgpt.com "Web Content Accessibility Guidelines (WCAG) 2.2"
[10]: https://web.dev/articles/vitals?utm_source=chatgpt.com "Web Vitals | Articles"
[16]: https://web.dev/blog/inp-cwv-launch?utm_source=chatgpt.com "Interaction to Next Paint is officially a Core Web Vital 🚀 | Blog"
