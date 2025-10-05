**요약(3–5줄)**
시각화(**Chart.js vs ECharts vs Recharts**), **OG 이미지 생성(서버 Satori/Sharp vs Headless-Chromium vs 외부 서비스)**, **집계 위치(BE vs FE vs Edge)**를 비교했습니다. **Chart.js + 서버측 Satori(OG)** + **집계는 백엔드 워커** 구성을 권고합니다. 평가는 유지보수/성능/보안·정합/생태계/학습곡선/릴리즈 빈도로 가중합했습니다. Chart.js의 **레이더/스캐터** 1st-party 문서와 **OGP** 권고를 근거로 합니다. ([chartjs.org][2])

```yaml
---
version: "1.0"
date: "2025-09-17"
owner: "PM: 이지율"
domains: ["backend", "frontend", "observability", "growth"]
source_of_truth: "DesignOptions.md"
use_browsing: true
---
```

### 1) 차트 라이브러리(가중치 총점)

| 후보               | 유지보수 | 성능 | A11y | 생태계 | 러닝 | 릴리즈 | **가중 합** |
| ------------------ | ------: | ---: | ---: | ----: | ---: | ----: | ---------: |
| **Chart.js(권고)** |   4.5   | 4.0  |  4.0 |   4.5 | 4.5  |  4.5  | **4.33**   |
| ECharts            |   4.0   | 4.5  |  3.5 |   4.0 | 3.5  |  4.0  | 4.00       |
| Recharts           |   4.0   | 3.5  |  3.5 |   4.0 | 4.0  |  4.0  | 3.83       |

> **근거:** Chart.js는 **레이더/스캐터** 1st-party 지원으로 구현 비용과 리스크를 줄입니다. ([chartjs.org][2])

### 2) OG 이미지 생성 옵션

| 옵션                     | 장점                         | 리스크/고려사항          | 비고                       |
| ------------------------ | ---------------------------- | ------------------------ | -------------------------- |
| **서버측 Satori/Sharp**  | 템플릿 제어, 수백 ms 응답    | 서버 부하 관리, 캐싱 필요 | 권고. 1200×630 권장. ([ogp.me][6]) |
| Headless-Chromium 캡처   | 픽셀 정합, CSS 100%          | 콜드스타트/메모리 부담   | Lambda 등은 비용↑          |
| 외부 서비스(Cloudinary) | 운영 간편, CDN 내장          | 비용·락인, 템플릿 제약    | 다이내믹 텍스트 안전. ([Cloudinary][5]) |

### 3) 집계 위치 비교

* **백엔드 워커(권고):** 일관성/보안/추적 용이, OTel로 계산·응답 모두 계측. ([opentelemetry-python-contrib][3])
* 프런트엔드: 지연↓이나 치트·무결성 리스크.
* Edge: 응답 빠르지만 복잡도↑, 멀티리전 상태 동기화 필요.

### 4) 광고 정책 준수 설계

* 버튼/내비/드롭다운과 **명확한 간격**(의도치 클릭 방지) 유지. Confirmed-Click 트리거 시 레이아웃 즉시 수정. ([Google Help][4])
* 슬롯 수 2–3개 내, Above the Fold 남용 금지. 정책 체크리스트로 리뷰. ([Google Help][4])

---

## 참고 문헌

[2]: https://www.chartjs.org/docs/latest/charts/radar.html "Radar Chart"  
[3]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[4]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[5]: https://cloudinary.com/blog/generating-dynamic-social-og-images "Generating Dynamic Social OG Images With Cloudinary"  
[6]: https://ogp.me/ "The Open Graph protocol"
