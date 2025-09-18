**요약(3?5줄)**
본 서비스는 **Self(본인) vs Others(타인의 눈)**을 비교해 **인지 격차(Perception Gap)**를 수치화·시각화합니다. MVP는 “**공통 24 + 관계 부스터 8 = 32문항**(Likert 1?5)”으로 시작하고, **Self 점수**와 **Other(연인/친구 N명) 집계**를 비교해 **GapScore·합의도(σ)**를 제공합니다. 결과는 **레이더/스캐터** 차트와 **공유용 OG 이미지**로 확산을 돕고, **RFC?9457 오류 포맷**, **WCAG?2.2 AA**, **Web Vitals(LCP≤2.5s/INP≤200ms/CLS≤0.1)** 기준을 준수합니다. **요청ID/OTel**을 기본값으로 계측합니다. ([RFC Editor][1])

```yaml
---
version: "1.0"
date: "2025-09-17"
product: "360Me ? Perception Gap (If I were you)"
domains: ["backend", "frontend", "growth"]
owner: "PM: 이지율"
source_of_truth: "PRD.md"
use_browsing: true
---
```

### 0) Assumptions(가정)

* **Stack:** FastAPI + PostgreSQL + Redis(백엔드), React + Vite + React Router + TanStack Query + Zustand(프론트), Chart.js(레이더/스캐터). ([chartjs.org][2])
* **표준:** 오류 응답 **RFC?9457**, 접근성 **WCAG?2.2 AA**, 성능 **Web Vitals**. ([RFC Editor][1])
* **프라이버시:** 집계 기준 **k≥3**(k-anonymity 원칙 차용)로 결과 공개, 원시 응답은 비식별 처리. ([EPIC][3])
* **법적 주의:** **MBTI/마이어스-브릭스**는 등록상표이며 **공식 문항/해설 불사용**(“MBTI-style” 언어만 사용). ([mbtionline.com][4])

### 1) 개요/비전/문제정의/타깃

* **컨셉:** *If I were you* ? “내가 너라면 이렇게 볼 거야.” Self vs Others 간 **Perception Gap**을 재밌고 안전하게 보여주는 **엔터테인먼트/셀프인사이트**.
* **핵심 가치:** ① **관계 맥락**(연인/친구) ② **다중 평가** 합의도/불일치 ③ **쉬운 공유**로 바이럴.
* **타깃:** 연인/친구/대학생·직장 초년생 중심 20?30대.

### 2) 범위/비범위

**In Scope:** 모드 선택, 문항(공통 24 + 부스터 8), Self 채점, 초대/응답 수집(N명), 집계/GapScore/합의도, 결과 시각화(레이더/스캐터), OG 공유 이미지, AdSense 안전 배치, RFC?9457 오류, OTel/Request-ID. ([RFC Editor][1])
**Out of Scope(이번 분기):** 조직/엔터프라이즈 권한, 유료 플랜, 모바일 앱, 고급 히트맵·관계 필터(차기).

### 3) 사용자 시나리오(요약)

* **S-1(커플):** 연인모드 32문항 → 파트너 1:1 초대 → **Self vs Partner 레이더/스캐터** → 공유 이미지.
* **S-2(친구 N):** 친구모드 링크 배포(익명/기명) → **Other 평균·σ·Gap** → “합의 높음/불일치 영역” 카드.
* **S-3(바이럴):** 3명 이상 응답 시 **추가 인사이트 해제** → OG 이미지로 SNS 공유 1클릭.
* **S-4(리텐션):** 만료 알림, 결과 PDF/링크 저장, **noindex/X-Robots-Tag**로 검색 노출 제어. ([Google for Developers][5])

### 4) 기능 요구(Functional Requirements)

| ID      | 요약              | 설명                            | 의존성   | 위험 | **수락 기준(요약)**                                                                  |
| ------- | ----------------- | ------------------------------- | ------ | --- | ----------------------------------------------------------------------------------- |
| R-101   | 모드 선택         | [연인/친구/기본]                | FE     | 오해 | 10초 내 첫 클릭→모드 진입률 ≥70%                                                     |
| R-102   | Self 테스트       | 공통 24 + 모드 8(32)            | R-101  | 이탈 | 완주율 ≥75%, 400/422는 **RFC?9457** 오류 구조. ([RFC Editor][1])                     |
| R-103   | 초대 링크         | 만료·최대인원·익명/기명·관계태그 | Auth/DB| 남용 | 링크 생성 201, 토큰 위조 방지, 429 레이트리밋                                        |
| R-104   | 타인 응답 제출    | 토큰 검증/중복제출 방지         | R-103  | 봇  | 동시 20명 P95<1s, 중복·봇 차단                                                        |
| R-105   | 집계/GapScore   | 가중평균, σ, Gap 계산          | R-102/104 | 편향 | 공식(§4.1/4.2)대로 계산, 단위테스트 100%                                               |
| R-106   | k-익명 공개 임계  | k<3 비공개                     | R-105  | 역추적 | k<3 결과 차트/공유 비활성화. ([EPIC][3])                                             |
| R-107   | 시각화            | 레이더(4축)/스캐터(2D)         | FE Charts | 과밀 | Chart.js 레이더·스캐터 구현, 모바일 30fps. ([chartjs.org][2])                        |
| R-108   | 공유 OG 이미지    | Self vs Other 요약·Gap 벡터    | FE/BE  | 성능 | 1200×630, 200ms 내 생성, 메타태그 정확. ([ogp.me][6])                                 |
| R-109   | 실시간 대시보드   | 응답 카운트/미리보기           | FE/BE  | 부하 | 3s 폴링(또는 SSE), 무한로드 방지                                                      |
| R-110   | AdSense 안전 슬롯 | 상단/본문중/하단 2?3개         | FE     | 정책 | 버튼/내비 근접 배치 금지, 정책 위반 0건. ([Google Help][7])                          |
| R-111   | 분석/바이럴 측정  | GA4 이벤트·UTM                 | FE     | 누락 | 시작/완료/초대/공유/조회 이벤트 로깅, UTM 규약 적용. ([Google for Developers][8])    |
| R-112   | 오류 표준화       | RFC?9457 문제상세(JSON)        | BE     | 누락 | 모든 4xx/5xx `type/title/status/detail/instance` 포함. ([RFC Editor][1])              |
| R-113   | 관측성            | X-Request-ID, OTel 트레이스    | BE/FE  | 누락 | 모든 요청 추적 가능, 자동 계측 가이드 준수. ([opentelemetry-python-contrib][9])     |
| R-114   | noindex 제어      | 결과/공유 링크 검색제외         | BE     | 유출 | `<meta name="robots" content="noindex">` 혹은 `X-Robots-Tag` 적용. ([Google for Developers][5]) |

### 5) 점수 계산 & 집계(공식)

**4.1 단일 평가자(Self/Other) ? 정규화**  
각 응답 `v∈{1..5}` → 편차 `d=v?3 ∈{?2..+2}`; `sign=+1(E/S/T/J), ?1(I/N/F/P)`  
지표합 `score_dim=Σ(sign_q·d_q)` → **정규화** `norm=score_dim/(2·n_dim_q) ∈[?1,+1]`.

**4.2 다중 평가자 집계(Other 평균·합의도·Gap)**  
관계 가중 `weight_r`(연인 1.5, 핵심친구 1.2, 기본 1.0)  
`other_norm_dim = (Σ_r w_r·norm_r) / Σ_r w_r`  
**합의도** `σ_dim = stdev({norm_r})`(낮을수록 일치)  
**인지 격차** `gap_dim = other_norm_dim ? self_norm_dim`  
**총괄 지표** `GapScore = mean(|gap_dim|)×100 (0..100)`.

### 6) NFR(수치+검증)

* **성능(백엔드):** 평균<500ms, **P95<1s**, 에러율<1%.
* **웹바이탈(75p):** **LCP≤2.5s / INP≤200ms / CLS≤0.1** ? 랩(Lighthouse)+필드(RUM/CrUX) 이중 검증. ([web.dev][10])
* **접근성:** **WCAG?2.2 AA**·APG 패턴, 포커스 표시·키보드 전탐색. ([W3C][11])
* **오류 표준화:** **RFC?9457** 고정 스키마 채택(7807 대체). ([RFC Editor][1])
* **관측성:** FastAPI OTel 자동계측·추적 조인 가능. ([opentelemetry-python-contrib][9])
* **광고 안전:** AdSense **의도치 클릭 방지**·위반 0건. ([Google Help][7])

### 7) 릴리즈 수락 기준

1. **E2E 5시나리오**(Self→초대→N 응답→집계→결과/공유) 무플레이크 합격.
2. Web Vitals(75p) 기준 통과(랩/필드). ([web.dev][10])
3. 모든 오류 응답이 **RFC?9457 JSON** 스키마. ([RFC Editor][1])
4. **k-익명 임계(k≥3)** 미만 결과 비공개 로직 검증. ([EPIC][3])
5. **AdSense 레이아웃 검사**(정책 페이지 체크리스트) 위반 0건. ([Google Help][7])

### 8) 보안/프라이버시

* 응답은 세션 토큰 기반, 최소 PII(닉네임 선택).
* 공개 공유는 요약 통계만, 개별 원응답/식별자 비노출(k-anonymity 사상). ([EPIC][3])
* 결과/공유 페이지에는 `noindex`/`X-Robots-Tag` 권장. ([Google for Developers][5])

### 9) 결과 시각화(차트)

* **레이더(4축: EI/SN/TF/JP)** ? Self/Other 평균 폴리곤.
* **스캐터(2D)** ? EI vs SN, TF vs JP 평면; 개별 평가자 점 플롯(최대 10 표시).
* **MVP:** Chart.js(공식 레이더/스캐터) → 추후 히트맵 플러그인/ECharts 고려. ([chartjs.org][2])

### 10) 엔드포인트(예)

`POST /api/self/submit`, `POST /api/invite/create`, `POST /api/other/submit`,  
`GET /api/result/{token}`, `GET /share/og/{token}.png`(OG 이미지). **오류는 RFC?9457**. ([RFC Editor][1])

### 11) 데이터 스키마(요약)

`users(id, nickname, created_at)`  
`sessions(id, user_id, mode, invite_token, is_anonymous, expires_at, max_raters)`  
`questions(id, dim, sign, text, context)`  
`responses_self(session_id, question_id, value)`  
`responses_other(session_id, rater_id?, relation_tag, question_id, value, created_at)`  
`aggregates(session_id, dim, self_norm, other_norm, gap, sigma, n_raters, updated_at)`

### 12) 마케팅/바이럴

* **언락 기제:** 평가자 **3명 이상** 도착 시 “추가 인사이트” 오픈.
* **공유:** OG 이미지 1200×630 권장, 주요 태그 `og:title/description/image/url`. ([ogp.me][6])
* **광고:** 상단 제목 아래 1, 본문 중단 1, 하단 1(2?3개), **클릭 유도/근접 배치 금지**. ([Google Help][7])

### 13) KPI/지표(Metrics)

* **M-101** Self 완료율, **M-102** 평균 응답자 수, **M-103** GapScore 중앙값, **M-104** 합의도(σ) 중앙값, **M-105** 공유 CTR, **M-106** OG 생성 성공률, **M-107** WebVitals(LCP/INP/CLS 75p), **M-108** RFC?9457 커버리지, **M-109** Confirmed-Click 발생률(0에 수렴), **M-110** k-임계 준수율. ([web.dev][10])

### 14) 테스트 케이스

* **T-101** Self 32문항 채점/정규화 정확성(경계값·무응답 처리)
* **T-102** Other 10동시 응답·중복 방지·P95<1s
* **T-103** 집계/가중치/σ/Gap 공식 단위·속성 테스트
* **T-104** 레이더/스캐터 렌더·모바일 성능(>30fps)
* **T-105** **k<3 차단** 및 공유 비활성화
* **T-106** RFC?9457 스냅샷(4xx/5xx) ([RFC Editor][1])
* **T-107** `noindex`/`X-Robots-Tag` 적용 확인(결과/공유) ([Google for Developers][5])
* **T-108** AdSense **의도치 클릭 방지** 규정 체크리스트 통과(버튼 근접 금지) ([Google Help][7])
* **T-109** OTel 트레이스-로그-요청ID 조인

### 15) Traceability(요구↔테스트↔지표)

| 요구(R)     | 테스트(T)        | 지표(M)         |
| ----------- | ---------------- | --------------- |
| R-102       | T-101/T-106      | M-101/M-108     |
| R-103/104   | T-102            | M-102/M-107     |
| R-105       | T-103            | M-103/M-104     |
| R-106       | T-105            | M-110           |
| R-107       | T-104            | M-107           |
| R-108       | T-104            | M-106/M-105     |
| R-110       | T-108            | M-109           |
| R-112/113/114 | T-106/T-109/T-107 | M-108/M-107    |

---

## 참고 문헌

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://www.chartjs.org/docs/latest/charts/radar.html "Radar Chart"  
[3]: https://epic.org/wp-content/uploads/privacy/reidentification/Sweeney_Article.pdf "k-ANONYMITY: A MODEL FOR PROTECTING PRIVACY"  
[4]: https://www.mbtionline.com/en-US/Legal "Legal"  
[5]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"  
[6]: https://ogp.me/ "The Open Graph protocol"  
[7]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[8]: https://developers.google.com/analytics/devguides/collection/ga4/reference/events "Recommended events | Google Analytics"  
[9]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[10]: https://web.dev/articles/vitals "Web Vitals | Articles"  
[11]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines (WCAG) 2.2"

