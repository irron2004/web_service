**요약**
시각화 라이브러리(Chart.js vs ECharts vs Recharts), **OG 이미지 생성(@vercel/og vs Playwright/Puppeteer)**, RUM/관측 구성을 비교했다. **MVP는 Chart.js(레이더/스캐터)** + **@vercel/og**(간단/고성능) 권고, 히트맵은 `chartjs-chart-matrix` 또는 **ECharts Heatmap**으로 확장한다. ([Chart.js][4])

```yaml
version: "0.9.0"
date: "2025-09-16"
domains: [frontend, backend, observability, growth]
owner: "PM/Tech Writer"
source_of_truth: ["PRD.md"]
```

### 1) 차트 라이브러리 비교(정량 매트릭스; 1~5점, 가중치: 유지보수 25/성능 25/보안 10/생태계 20/학습 10/릴리즈빈도 10)

| 후보           | 유지보수 | 성능 | 보안 | 생태계 | 학습 | 릴리즈 |      합계 |
| ------------ | ---: | -: | -: | --: | -: | --: | ------: |
| **Chart.js** |    5 |  4 |  4 |   5 |  5 |   5 | **4.7** |
| **ECharts**  |    4 |  5 |  4 |   4 |  3 |   4 |     4.3 |
| **Recharts** |    4 |  3 |  4 |   4 |  4 |   4 |     3.9 |

* **근거**: Chart.js는 레이더/스캐터 문서 및 트리셰이킹/플러그인 생태계 탄탄. 히트맵은 `chartjs-chart-matrix`로 보완하거나, 데이터가 커지면 ECharts Heatmap으로 이관. ([Chart.js][4])

### 2) OG 이미지 생성

| 후보                 | 장점                               | 유의                      | 근거                 |
| ------------------ | -------------------------------- | ----------------------- | ------------------ |
| **@vercel/og**(권고) | HTML/CSS로 즉시 이미지, Edge 대응, 간단 배포 | Vercel 런타임 전제(대안: Node) | ([Vercel][13])     |
| Playwright         | SSR 캡처 정밀, PNG 품질/투명 지원          | 브라우저 부팅/콜드스타트           | ([Playwright][14]) |
| Puppeteer          | 친숙한 생태계/예제 풍부                    | 람다 번들/콜드스타트             | ([CheatCode][15])  |

### 3) 관측/분석

* **OTel FastAPI 자동계측**, GA4 **이벤트 네이밍 규칙(영문/언더스코어/예약 접두어 금지)** 적용. ([opentelemetry-python-contrib.readthedocs.io][2])

### 권고안 & 트레이드오프

* **권고**: *Chart.js(레이더/스캐터) + @vercel/og* → 간결·빠른 MVP, 추후 히트맵은 ECharts로 업그레이드.
* **트레이드오프**: ECharts는 대규모/특수 시각화에 강하지만 초기 러닝/번들 부담. Playwright/Puppeteer는 파워풀하나 운영 오버헤드.

[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html?utm_source=chatgpt.com "OpenTelemetry FastAPI Instrumentation"
[4]: https://www.chartjs.org/docs/latest/charts/radar.html?utm_source=chatgpt.com "Radar Chart"
[13]: https://vercel.com/docs/og-image-generation?utm_source=chatgpt.com "Open Graph (OG) Image Generation"
[14]: https://playwright.dev/docs/screenshots?utm_source=chatgpt.com "Screenshots"
[15]: https://cheatcode.co/blog/how-to-convert-html-to-an-image-using-puppeteer-in-node-js?utm_source=chatgpt.com "How to Convert HTML to an Image Using Puppeteer in ..."
