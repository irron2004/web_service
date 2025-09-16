**요약(3–5줄)**
연인/친구가 보는 ‘나’와 스스로 인식한 ‘나’를 비교해 **인지 격차(Perception Gap)**를 수치화·시각화하는 웹 서비스다. **공통 24문항 + 관계별 8문항**으로 EI/SN/TF/JP 점수를 산출하고, 다중 평가(여러 친구) 집계로 **합의도(σ)**와 **GapScore**를 제공한다. 1차 시각화는 **레이더 + 스캐터(Chart.js)**, 결과는 **OG 이미지**로 손쉽게 공유한다. 백엔드는 FastAPI, 프론트는 React(Vite)로 구현하며 **RFC 9457 오류 JSON**, **Web Vitals 임계(LCP≤2.5s/INP≤200ms/CLS≤0.1)**, **WCAG 2.2 AA**를 준수한다. ([RFC Editor][1])

```yaml
version: "0.9.0"
date: "2025-09-16"
domains: [backend, react, analytics, growth]
owner: "PM/Tech Writer"
source_of_truth: ["이 PRD", "DesignOptions.md", "Tasks.md"]
```

### 0) Assumptions(가정)

* Stack: **FastAPI + PostgreSQL + Redis + OTel**, **React + Vite + React Router + TanStack Query + Zustand**. ([opentelemetry-python-contrib.readthedocs.io][2])
* Use_Browsing: yes(표준 인용 포함).
* 개인정보/KR: 이메일, 닉네임(선택: 연령대). 민감정보·심리검사 결과의 **원문 응답은 비식별 저장**(세션 단위 토큰)·삭제권 보장.
* **MBTI 공식 문항/해설/상표 미사용**. ‘MBTI’ 등은 Myers & Briggs Foundation의 상표임을 고지. ([mbtionline.com][3])

### 1) 비전/핵심 가치/문제정의

* **If I were you**: “내가 너라면 이렇게 볼 거야.”
* 핵심 가치: (1) **관계 맥락**(연인/친구) 반영 문항, (2) **다중 평가 합의도/불일치** 시각화, (3) **쉬운 공유**로 바이럴.
* 문제: 자기확증 편향으로 **자기-타자 인식 격차**가 커짐 → **안전하고 구조화된 피드백** 필요.

### 2) 범위/비범위

**In scope(MVP)**: 모드선택(연인/친구/기본), **Self 24(+8)** 응답, **타인 링크 초대/익명**, 집계/시각화(레이더·스캐터), **OG 공유**, 간단한 인사이트 카드, **AdSense 슬롯(최대 3)**.
**Out**: 앱(모바일), 조직형 권한, 유료결제, 고급 분석(히트맵/바이올린은 차기), 커스텀 AI 대화요약.

### 3) 사용자 플로우(IA)

```
랜딩 → [연인/친구/기본] 선택
 → (선택) Self 24(+8) 문항 → Self 점수
 → 타인 링크 생성(만료, 익명/기명) → 응답 수집 대시보드
 → 결과(레이더/스캐터, 합의도, GapScore) → 공유(OG 이미지)
```

### 4) 문항 설계

* **공통 24문항**: EI/SN/TF/JP 각 6. Likert 1–5.
* **부스터 8문항**: 연인/친구 별 프리셋(요청안 반영).
* **채점 부호**: (E,S,T,J)=+1, (I,N,F,P)=-1.

> *MVP: 24 + 8 = 32문항(파일럿 후 24–40 최적화).*

### 5) 점수 계산(단일 평가자)

* 각 응답 `v∈{1..5}` → **편차** `d=v-3 ∈ {-2..+2}`
* 지표별 합 `score_dim = Σ(sign_q * d_q)`
* **정규화** `norm = score_dim / (2 * n_dim_q)` → **[-1,+1]**

### 6) 다중 평가 집계

* 평가자 r의 가중치 `weight_r`(기본 1.0, 연인 1.5, 핵심친구 1.2 옵션)
* **Other 평균** `other_norm_dim = (Σ weight_r*norm_r) / Σ weight_r`
* **합의도** `σ_dim`(표준편차)
* **인지 격차** `gap_dim = other_norm_dim - self_norm_dim`
* **GapScore** `= mean(|gap_dim|) × 100` (0–100)

### 7) 시각화(Chart.js)

* **레이더(EI/SN/TF/JP, 0–100 변환)**: Self vs Other 평균, (옵션) 개별 라인 샘플링.
* **스캐터**: (EI vs SN) / (TF vs JP) 평면, Self·Other·개별 분포.
* 차기: **히트맵(분포)** → `chartjs-chart-matrix` 또는 ECharts Heatmap. ([Chart.js][4])

### 8) 기능 요구(추적성 표)

| **ID**    | 요약         | 설명                              | 의존성       | 위험    | **수락 기준(요약)**                                                            |
| --------- | ---------- | ------------------------------- | --------- | ----- | ------------------------------------------------------------------------ |
| **R-101** | 모드 선택      | 연인/친구/기본 모드 라우팅                 | FE Router | 혼란    | 라우팅/URL 쿼리 유지, Lighthouse A11y≥90                                        |
| **R-102** | Self 응답·채점 | 공통24+모드8 채점/정규화                 | R-101     | 품질    | 샘플 입력→지표별 norm 정확(단위테스트 통과)                                              |
| **R-103** | 초대 링크      | 만료/최대인원/익명 설정, 토큰 생성            | Auth/DB   | 오남용   | 201 생성, 만료/상한 동작, 토큰 1회용                                                 |
| **R-104** | 타인 응답 수집   | 비정상 응답 방지(속도, 중복)               | R-103     | 스팸    | 10명 동시 응답 P95<1s, 중복 차단, 429 핸들링 ([IETF Datatracker][5])                 |
| **R-105** | 집계/통계      | other_norm, σ, GapScore        | R-102/104 | 왜곡    | 가중치 적용/숫자 안정성 검증(경계값 테스트)                                                |
| **R-106** | 시각화        | 레이더+스캐터(Chart.js)               | FE Chart  | 성능    | 60fps, 캔버스 리사이즈 안정, 샘플 10명 표시 ([Chart.js][4])                            |
| **R-107** | 관계 필터      | 전체/연인/친구/태그 필터                  | R-104/105 | 복잡성   | 필터 전환<100ms, 결과 일관성                                                      |
| **R-108** | 공유(OG)     | 결과 요약 OG 이미지/링크 생성              | R-106     | 저작권   | 200 생성, **noindex** 메타 적용 권장 ([ogp.me][6])                               |
| **R-109** | 프라이버시      | **친구 집계는 n≥3** 공개, 1:1 연인은 쌍 비교 | Auth      | 역추적   | 임계 위반시 블러/비공개                                                            |
| **R-110** | AdSense    | 결과 상단/중단/하단 ≤3개, 정책 준수          | FE/BE     | 실수 클릭 | 버튼 근접 배치 금지, 정책 체크리스트 통과 ([Google Help][7])                              |
| **R-111** | 분석/바이럴     | GA4 이벤트/UTM, 공유전환 측정            | FE        | 명명    | **영문소문자/언더스코어** 규칙 준수 ([Google Help][8])                                 |
| **R-112** | 관측성        | OTel 트레이스/메트릭, X-Request-ID     | Infra     | 누락    | FastAPI 자동계측, 대시보드 연결 ([opentelemetry-python-contrib.readthedocs.io][2]) |
| **R-113** | 오류 표준      | **RFC 9457 Problem Details**    | BE        | 누락    | 모든 4xx/5xx 스키마 통일(계약 테스트) ([RFC Editor][1])                              |
| **R-114** | 레이트리밋      | IP/세션별 한도, 429 + Retry-After    | BE/Edge   | 차단    | 헤더/바디에 정책 안내(문서화) ([IETF Datatracker][5])                                |
| **R-115** | 대시보드       | 실시간 응답 카운트/미리보기                 | R-104     | 조작    | 지연<1s, 폴링/ SSE 중 택1                                                      |
| **R-116** | 접근성        | **WCAG 2.2 AA**                 | FE        | 미준수   | 키보드 100%, 대비≥4.5:1 ([W3C][9])                                            |

### 9) API 설계(발췌)

* `POST /api/self/submit` → `{answers:[{qid, value}]}` → `{self_norm:{EI,SN,TF,JP}}`
* `POST /api/invite/create` → `{mode, expires_at, max_n, anonymous}` → `{invite_token}`
* `POST /api/other/submit` → `{invite_token, relation_tag?, answers:[...]}`
* `GET /api/result/{token}` → `{self_norm, other_norm, gap, sigma, n, weights}`
* 오류: **RFC 9457 Problem Details** JSON (`type/title/status/detail/instance`) 사용. ([RFC Editor][1])

### 10) 데이터 스키마(요약 DDL)

```sql
create table users (
  id bigserial primary key,
  email citext unique,
  nickname text,
  created_at timestamptz default now()
);
create table sessions (
  id uuid primary key,
  owner_id bigint references users(id),
  mode text check (mode in ('basic','couple','friend')),
  invite_token text unique not null,
  is_anonymous boolean default true,
  expires_at timestamptz not null,
  max_raters int default 50,
  created_at timestamptz default now()
);
create table questions (
  id serial primary key,
  dim text check (dim in ('EI','SN','TF','JP')),
  sign smallint check (sign in (-1,1)),
  context text check (context in ('common','couple','friend')),
  text text not null
);
create table responses_self (
  session_id uuid references sessions(id),
  question_id int references questions(id),
  value smallint check (value between 1 and 5),
  primary key(session_id, question_id)
);
create table responses_other (
  session_id uuid references sessions(id),
  rater_hash text, -- 비식별
  relation_tag text,
  question_id int references questions(id),
  value smallint check (value between 1 and 5),
  created_at timestamptz default now(),
  primary key(session_id, rater_hash, question_id)
);
create table aggregates (
  session_id uuid primary key references sessions(id),
  ei_self real, sn_self real, tf_self real, jp_self real,
  ei_other real, sn_other real, tf_other real, jp_other real,
  ei_gap real, sn_gap real, tf_gap real, jp_gap real,
  ei_sigma real, sn_sigma real, tf_sigma real, jp_sigma real,
  n int, gap_score real
);
```

### 11) 비기능 요구(NFR, 수치+검증)

* 가용성 **99.9%/월**.
* 백엔드 성능: 평균<**500ms**, P95<**1s**(핵심 API). 에러율<**1%**.
* 웹바이탈(75p): **LCP≤2.5s / INP≤200ms / CLS≤0.1**. INP는 2024.3 Core Web Vitals로 FID를 대체. ([web.dev][10])
* 보안: **OWASP ASVS v5.0 L2** 기준 점검. ([OWASP Foundation][11])
* 접근성: **WCAG 2.2 AA**. ([W3C][9])
* 오류 표준: **RFC 9457**. ([RFC Editor][1])
* 관측성: OTel 자동계측(FastAPI), **X-Request-ID** 전 구간 전파. ([opentelemetry-python-contrib.readthedocs.io][2])

### 12) 릴리즈 수락 기준

1. 핵심 플로우 5개 E2E(랜딩→모드→Self→초대→3인 집계→결과) **무플레이크**.
2. Web Vitals 75p **합격**(Lighthouse 랩 + RUM 필드). ([web.dev][10])
3. 모든 4xx/5xx는 **RFC 9457 JSON** 스키마로 계약 테스트 통과. ([RFC Editor][1])
4. **ASVS v5.0 L2** 체크리스트 100% 기록, 차단급 취약점 0건. ([OWASP Foundation][11])
5. OTel 대시보드에서 **요청↔트레이스↔로그** 상호탐색(X-Request-ID) 가능. ([opentelemetry-python-contrib.readthedocs.io][2])
6. AdSense **배치 정책** 위반 없음(버튼 근접 금지/유도 금지). ([Google Help][7])

### 13) 리스크/완화

* **악성 응답/봇**: 속도<0.3s·패턴 탐지, IP/토큰 한도, 429/Retry-After. ([IETF Datatracker][5])
* **프라이버시**: 친구 n<3 비공개, 결과 페이지 **noindex** 권장. ([Google for Developers][12])
* **상표/저작권**: MBTI 상표 고지, 공식 문항·해설 미사용. ([mbtionline.com][3])
* **정서적 영향**: 결과 문구 가이드(비난/낙인 금지)·신고/가림.

### 14) KPI

* Activation: Self 완료율, 초대 생성율, 최초 타인응답 도착율
* Engagement: 평균 응답자 수/세션, 공유 클릭률, **Gap 인사이트 열람율**
* Viral(K): 1인당 초대 수 × 초대 전환율
* Monetize: 페이지 RPM/가시성(Active View) 추적

### 15) Ask 게이트(승인 필요 변경)

* (a) **공개 API/스키마 변경**(외부 소비 시), (b) **레이트리밋 정책 변경**, (c) **AdSense 슬롯/정책 변경**, (d) **데이터 보존기간 변경**.

### 16) 추적성 교차표(R↔T↔M)

* **R-102(Self 채점)** ↔ **T-102(채점 정규화 경계값/속성 기반 테스트)** ↔ **M-102(채점 오류율, 평균 처리시간)**
* **R-105(집계/GapScore)** ↔ **T-105(가중치/표준편차/영(0)·최대값 시나리오)** ↔ **M-105(GapScore 분포, σ 평균)**
* **R-106(시각화)** ↔ **T-106(Canvas 리사이즈/샘플링/스크린리더)** ↔ **M-106(프론트 렌더시간, INP/LCP)**
* **R-108(공유/OG)** ↔ **T-108(OG Validator/이미지 생성 성공률)** ↔ **M-108(공유 CTR, 이미지 생성 P95)**
* **R-110(AdSense)** ↔ **T-110(버튼 근접/유도 문구 없음 시각검수)** ↔ **M-110(Invalid CTR 비율)**

---

[1]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[2]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html?utm_source=chatgpt.com "OpenTelemetry FastAPI Instrumentation"
[3]: https://www.mbtionline.com/en-US/Legal?utm_source=chatgpt.com "Legal"
[4]: https://www.chartjs.org/docs/latest/charts/radar.html?utm_source=chatgpt.com "Radar Chart"
[5]: https://datatracker.ietf.org/doc/html/rfc6585?utm_source=chatgpt.com "RFC 6585 - Additional HTTP Status Codes"
[6]: https://ogp.me/?utm_source=chatgpt.com "The Open Graph protocol"
[7]: https://support.google.com/adsense/answer/1346295?hl=en&utm_source=chatgpt.com "Ad placement policies - Google AdSense Help"
[8]: https://support.google.com/analytics/answer/13316687?hl=en&utm_source=chatgpt.com "[GA4] Event naming rules - Analytics Help"
[9]: https://www.w3.org/TR/WCAG22/?utm_source=chatgpt.com "Web Content Accessibility Guidelines (WCAG) 2.2"
[10]: https://web.dev/articles/vitals?utm_source=chatgpt.com "Web Vitals | Articles"
[11]: https://owasp.org/www-project-application-security-verification-standard/?utm_source=chatgpt.com "OWASP Application Security Verification Standard (ASVS)"
[12]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag?utm_source=chatgpt.com "Robots Meta Tags Specifications | Google Search Central"
