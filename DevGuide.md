## DevGuide.md — 개발 지침서 (스택·아키텍처·계측·테스트)

**요약 (3–5줄)**
Python-first 원칙으로 FastAPI + PostgreSQL을 중심에 두고, 채점/Δ/플래그를 단일 참조 모듈(`core_scoring`)로 구현합니다. 모든 결과는 결정 패킷으로 봉인하고, RFC 9457 오류·X-Request-ID·OpenTelemetry 계측을 전 구간 적용합니다. 프런트엔드는 React + TypeScript + Vite와 Chart.js로 시각화를 담당하며, 민감 정보는 noindex와 토큰 만료로 보호합니다.

```yaml
---
version: "1.0"
date: "2025-09-19"
audience: ["Backend", "Frontend", "Data", "QA", "Ops"]
owner: "Tech Lead: 이지율"
source_of_truth: "DevGuide.md"
---
```

### 1) 코딩 스택 (무엇으로 만드는가)

- Backend: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Redis (Rate-limit/Queue)
- Frontend: React + TypeScript + Vite, React Router, TanStack Query(서버 상태), Zustand(로컬 상태), Chart.js
- Database: PostgreSQL, (옵션) pgvector(추후 추천/유사도)
- Infra: Cloud Run(컨테이너), Cloud SQL(Postgres), Cloudflare(Pages/CDN/WAF)
- Observability: OpenTelemetry(Trace/Metric/Log), 구조화 JSON 로깅

---

### 2) 아키텍처 (모듈러 모놀리식)

- 도메인 모듈: `auth`, `consent`, `session`, `survey`, `scoring`, `insight`, `safety`, `share`
- 워커: PDF 생성·알림·안전 점검 큐(Celery 또는 RQ)
- BFF 패턴: 프런트가 요구하는 합성 응답을 `/bff/*`에서 제공

---

### 3) 데이터 모델 (요약 DDL)

```sql
-- 사용자/세션
users(id pk, email?, nickname, created_at)
couple_links(id pk, a_user_id fk, b_user_id fk, status, created_at)

sessions(id pk, owner_id fk, stage enum(1,2,3), token unique, expires_at, created_at)

-- 1단계 집계 (타인이 보는 남편) : k-익명 상태 포함
others_ratings(session_id fk, subject_user_id fk, dim text, norm float, rater_tag text, created_at)
others_aggregate(session_id fk, dim text, other_norm float, k int, updated_at)

-- 2·3단계 설문 (SELF/GUESS)
questions(id pk, code text, dim text, reverse bool, scale text, context text)
responses(session_id fk, respondent enum('A','B'), code text, self smallint, guess smallint, created_at)

-- 스코어/Δ/플래그
scores(session_id fk, respondent enum, dim text, mean_self float, mean_guess float, delta float)
flags(session_id fk, code text, severity enum('low','mid','high'), reason text)

-- 시나리오/서술형
scenarios(session_id fk, code text, choice text, note text)
free_text(session_id fk, key text, text_encrypted bytea)

-- 결정 패킷 (포렌식)
decision_packets(id pk, session_id fk, packet_sha256 bytea, storage_url text, code_ref text, model_id text, created_at)
audit_events(id pk, ts timestamptz, req_id uuid, actor text, event_type text, payload jsonb, prev_hash bytea, hash bytea, code_ref text)
```

---

### 4) 채점·Δ·플래그 (참조 구현; 단일 모듈)

```python
# core_scoring/__init__.py
from statistics import pstdev

REV = {"CB1","CB2","CB3","CB4","PD1","PD2"}   # 역채점
SCALES = {
  "CS": ["CS1","CS2","CS3","CS4","CS5","CS6"],
  "EA": ["EA1","EA2","EA3","EA4","EA5","EA6"],
  "CB": ["CB1","CB2","CB3","CB4","CB5","CB6"],
  "PD": ["PD1","PD2","PD3","PD4"],
  "RP": ["RP1","RP2","RP3","RP4","RP5","RP6"],
  "LF": ["LF1","LF2","LF3","LF4","LF5","LF6"],
  "IN": ["IN1","IN2","IN3","IN4","IN5","IN6"],
  "SF": ["SF1","SF2","SF3","SF4","SF5","SF6"],
}

def score_item(code: str, v: int) -> float:
    if code in REV:
        return 4 - v
    return v

def scale_mean(scale: list[str], answers: dict[str, int]) -> float:
    vals = [score_item(c, answers[c]) for c in scale if c in answers]
    return sum(vals) / len(vals)

def compute_deltas(a_self: dict, a_guess: dict, b_self: dict, b_guess: dict):
    # ΔA: |A.GUESS - B.SELF|, ΔB: |B.GUESS - A.SELF|
    deltaA = {c: abs(a_guess[c] - b_self[c]) for c in a_guess if c in b_self}
    deltaB = {c: abs(b_guess[c] - a_self[c]) for c in b_guess if c in a_self}
    return deltaA, deltaB

def delta_by_scale(delta: dict) -> dict:
    out = {}
    for key, items in SCALES.items():
        ds = [delta[c] for c in items if c in delta]
        out[key] = sum(ds) / len(ds) if ds else 0.0
        
    return out

def flag_rules(scales: dict, raw: dict) -> list[dict]:
    flags = []
    if raw.get("CS2", 5) <= 2 or raw.get("IN4", 5) <= 2:
        flags.append({"code": "SAFETY", "severity": "high", "reason": "존중/거절 문제"})
    if raw.get("PD1", 0) >= 3 and raw.get("PD3", 0) >= 3:
        flags.append({"code": "PURSUIT_WITHDRAW", "severity": "mid", "reason": "추궁–회피 패턴"})
    if sum(int(raw.get(x, 0) >= 3) for x in ["CB1","CB2","CB3","CB4"]) >= 2:
        flags.append({"code": "COGNITIVE", "severity": "mid", "reason": "흑백사고/마음읽기"})
    # ... 추가 룰
    return flags
```

원칙: 이 모듈을 FE/BE/워커가 동일 버전으로 사용하고, 결과 저장 시 `code_ref`(Git SHA)와 함께 decision_packet에 해시 봉인합니다.

---

### 5) API (요약; 오류 = RFC 9457, 요청 ID 전파)

- `POST /v1/sessions` → 세션 생성(단계/토큰/만료)
- `POST /v1/answers/{session_id}` → SELF/GUESS 배치 저장(부분 저장 허용)
- `POST /v1/compute/{session_id}` → 채점·Δ·플래그·결정 패킷 생성
- `GET /v1/result/{session_token}` → 레이더/Δ/플래그/코칭 요약(민감 텍스트 제외)
- `GET /v1/pdf/{session_token}` → 결과 PDF(워터마크, noindex)
- `POST /v1/others/import` → 1단계 집계 업서트(k 상태 포함)
- 오류 포맷: `{ "type", "title", "status", "detail", "instance", "errors?" }`

헤더 규약: 수신 X-Request-ID 없으면 발급 후 응답 헤더 반영, 로그/트레이스 전파. 민감 결과는 `Cache-Control: private, no-store`.

---

### 6) 프런트엔드 구현 가이드

- 폼: 32문항(8×4), 8문항씩 페이지네이션, 라디오 0–4(키보드 접근성 확보)
- 차트: Chart.js 레이더(8축) + Δ 히트맵(행=척도, 열=문항; 모바일은 리스트로 폴백)
- 상태: TanStack Query – 자동 캐싱/재검증, 로딩 스켈레톤 제공
- 안전 UI: k<3 잠금 카드, 위험 플래그 시 상단 고정 안내(연계 링크)
- 공유: 기본 비활성, 필요 시 요약형(개인·민감 제거)만 허용

---

### 7) 보안·프라이버시

- PII 최소화: 닉네임/관계 수준만, 생년월일·주소 수집 금지
- 암호화: 전송/TDE, 서술형 텍스트는 필드 레벨 암호화
- 접근 제어: 세션 토큰 범위 최소화(작성자/배우자만 접근)
- k-익명: 1단계 집계는 k≥3 공개, 아니면 잠금 처리
- 로봇/색인 차단: 결과·공유 URL noindex, 토큰 만료/무효화

---

### 8) 포렌식/감사 (증거가능성)

- Audit Event: `who/what/when/why`, `code_ref`, `model_id/prompt_id`, `prev_hash` → `hash` 체인
- Decision Packet: 입력(응답 스냅샷)·코드 버전·출력(점수/Δ/플래그)·해시를 WORM 스토리지에 저장
- Re-run: 과거 `code_ref`로 재실행 후 diff 로그 생성(검증/분쟁 대비)

---

### 9) 테스트·품질

- 단위: 채점/역채점/Δ/플래그(경계·무응답)
- 통합: DB 트랜잭션·PDF·알림·k 규칙
- E2E (Playwright): 5 플로우(작성 → 중단 → 복구 → 계산 → 결과) 무플레이크
- 성능/부하: k6 RPS 점증, API P95 <1s
- 접근성: 키보드/포커스/대비 자동·수동 검증
- 보안: Rate-limit, 토큰 재사용 감지, 민감 링크 강제 만료

---

### 10) 배포/운영

- CI/CD: GitHub Actions → 테스트 → 스캔 → 스테이징 → 카나리(10 → 50 → 100)
- 런타임: Cloud Run(리비전/롤백), Cloud SQL, Cloudflare(Pages/WAF)
- 관측: OTel 트레이스(요청-DB-워커), 대시보드에 리비전별 P95/에러율 표기
- 알림: 고위험 Δ 급증·안전 안내 클릭률 급감 시 경보 룰

---

### 11) LLM/ML 사용 지침 (옵션)

- 삽입 지점: Top-3 요약, 시나리오 해설, 주간 과제 제안
- 가드레일: 컨텍스트는 수치·규칙만 주입, 금칙어/PII 필터, 실패 시 템플릿 폴백
- 버저닝: `model_id`, `prompt_id`, `input_hash`, `output_hash`, 토큰 사용량 저장

---

### 12) 엣지 케이스

- 무응답/부분 저장: 결측은 제외 평균, Δ 계산 시 공통 문항만 사용
- 극단값: 동일 값 반복 응답(봇 의심) → 신뢰도 낮춤 경고(내부 가중치)
- 시나리오 자유 서술 과도 길이: 500자 제한 + 요약 프리뷰

---

### 13) 디자인·카피 합의 (요약)

- 단정형 금지(“당신은 ∼형이다” X), 수치·표본·시점 병기
- 위험/민감 주제 상단 경고 배너 고정
- 버튼 문구는 행동 지향(“타임아웃 합의 연습하기”)

---

### 14) QA 체크리스트 (출시 게이트)

- [ ] Δ·역채점·플래그 스냅샷 테스트 통과
- [ ] k<3 잠금·안전 안내 동작 확인
- [ ] RFC 9457 오류·요청 ID·OTel 조인 검증
- [ ] LCP/INP/CLS 목표 달성 (랩 + 필드)
- [ ] PDF/noindex, 토큰 만료 확인
- [ ] Decision Packet 해시 검증 성공

---

### 부록 A. API 오류 예시

```json
{
  "type": "https://api.360me.app/errors/validation",
  "title": "Validation Failed",
  "status": 422,
  "detail": "field `CS2.self` is required",
  "instance": "/v1/answers/abc123",
  "errors": {"CS2.self": ["required"]}
}
```

### 부록 B. 결과 JSON 예시

```json
{
  "session_id": "abc123",
  "scales": {"CS": {"selfA": 3.2, "selfB": 2.8, "deltaA": 0.7, "deltaB": 1.4}},
  "top_delta_items": ["PD1", "CS3", "LF2"],
  "flags": [{"code": "PURSUIT_WITHDRAW", "severity": "mid"}],
  "insights": [{"title": "타임아웃 합의", "action": "20분 후 재개 약속"}],
  "k_state": {"others": {"k": 5, "visible": true}}
}
```

