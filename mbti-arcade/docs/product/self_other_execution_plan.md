# Self/Other Schema & Intake Execution Guide

문서는 트랙 A~E로 나눈 백엔드/프런트/관측/QA/문서 작업을 한 번에 착수할 수 있도록 기획·개발 관점의 세부 지시서를 모은다. 모든 카피·라벨·관계 라디오 옵션은 PageContentSpec 및 review_todo.md와 일치해야 한다.

---

## Track A · Backend Schema & APIs

### Task A1 — Finalize self/other schema migration

**기획**
- **입력**: 관계 라벨(`친구·동료·연인·가족·기타` ↔ enum `friend|coworker|partner|family|other`), PII 정책(닉네임 선택·이메일 비수집), 세션 스냅샷 필드(표시명/아바타/MBTI 공개 범위) 확인.
- **산출물**: 데이터 사전(새 컬럼 정의, 라벨↔enum 매핑), 마이그레이션 운영 계획(읽기/쓰기 병행, 롤백 전략).
- **세부 작업**: ParticipantRelation 표시 라벨 확정, snapshot 필드 노출 한계 정의, `core_scoring` 참조 필드 존치/폐기 정리.
- **DoD**: `docs/self_other_schema_transaction.md`에 필드 설명·라벨·노출 정책·이행 단계 반영, 관계 라디오 옵션과 enum 매핑 1:1 일치.
- **테스트**: “동료” 선택→`coworker` 저장/노출 스냅샷.

**개발**
- **입력**: ORM 초안, 기존 스키마, Alembic 환경.
- **산출물**: Alembic rev.003(up/down) + 백필 훅, ORM 필드 정합 검증.
- **세부 작업**:
  1. 스키마 변경 — `participants.relation(enum)`, `participants.nickname`, `participant_answers.items/created_at`, `sessions.snapshot_owner_*` 등.
  2. Alembic upgrade/downgrade 작성, 기존 행 백필(`relation='other'`), 제약 추가·해제 순서 관리.
  3. ORM 매핑 테스트(Reflection) 및 `model_config = ConfigDict(protected_namespaces=())` 경고 제거.
- **DoD**: 마이그레이션 양방향 스모크(테스트 DB) 성공, 체크 제약·Enum 검증 통과.
- **테스트**: upgrade→insert 샘플→downgrade→재upgrade, ORM↔DDL 매핑 테스트.

### Task A2 — Participant intake & answers APIs

**기획**
- **입력**: 관계 라디오/닉네임 필드, max_raters 정책(기본 50), 중복 참여 금지 규칙.
- **산출물**: UX 에러 카피(정원 초과/중복/만료/토큰 오류), 응답 후 전환 흐름 정의.
- **세부 작업**: 라디오 옵션 순서/툴팁, 32문항 범위(1~5) 규칙.
- **DoD**: 카피가 PageContentSpec 일치, 모든 에러 케이스 사용자형 톤 확보.
- **테스트**: 정원 초과/중복/토큰 오류 UI 스냅샷.

**개발**
- **입력**: `testing_utils.build_fake_answers`.
- **산출물**: FastAPI 라우터, 스키마, 통합 테스트.
- **세부 작업**: 
  - `POST /v1/participants/{token}` — max_raters·중복 가드, RFC9457 문제 응답(409/403/404).
  - `POST /v1/answers/{participant_id}` — 32문항·1~5 검증, 저장 후 집계 큐 트리거.
  - 공통 ProblemDetails 포맷 유지, rater_hash 임시 로직 제거.
- **DoD**: 정상/정원/중복/형식오류/토큰불가 테스트 통과, 공개 페이지 개발 용어 0건 유지.
- **테스트**: 길이 31/32/33, 값 0/6 오류, 중복 제출 409 확인.

### Task A3 — Relation aggregates & k≥3 enforcement

**기획**
- **입력**: 4축 정의(EI/SN/TF/JP), PGI/Confidence 산식 초안, 잠금 정책(k<3 잠금).
- **산출물**: 결과 페이지 설명 카피, 잠금/해금 안내, 카드 구성(Top/비율/Gap/Confidence).
- **세부 작업**: 캐시 TTL 및 무효화 조건(answers 저장 시), 프리뷰 vs 풀 리포트 구분.
- **DoD**: k<3 잠금 카드, k≥3 레이더·Top/Gap 노출, 잠금 안내 문구.
- **테스트**: n=0/1/2/3 UI/값 스냅샷.

**개발**
- **산출물**: 집계 서비스( relation_aggregates, PGI/Confidence 포함), 캐시, API(`GET /v1/participants/{token}/preview`, `GET /v1/report/{token}`).
- **세부 작업**: 집계 시 unlock 플래그 갱신, 축 정규화(0~100), 캐시 키/무효화 관리.
- **DoD**: 3번째 응답에서 unlock, 리포트 200, 성능 p95<100ms(캐시 히트 기준).
- **테스트**: Gap·분포·잠금 분기 스냅샷.

---

## Track B · Frontend Flows & Copy

### Task B1 — Owner profile & CTA flow

**기획**: 표시명/아바타/MBTI 필드 카피, 토글 기본 ON, 랜딩 CTA/단계 설명 업데이트.
**개발**: OwnerProfile 화면, `/v1/profile` 저장 후 초대 화면, 접근성 라벨/포커스, Lighthouse A11y≥90.
**테스트**: 빈 표시명은 허용, MBTI 미선택 시 자체검사 경로 분기.

### Task B2 — Respondent intake & friend form cleanup

**기획**: 이메일 문구 제거, 익명 배지 규칙.
**개발**: 라디오+닉네임 폼, 제출 후 프리뷰 호출, 템플릿 상태 갱신, UI 1클릭 연결.
**테스트**: 닉네임 공백/이모지 처리.

### Task B3 — Self-test UX upgrade

**기획**: 8×4 페이지 구성, 키보드 안내, 완료 CTA.
**개발**: 페이지네이션/키 이벤트/포커스 링, 완료 후 profile로 이동, 스켈레톤/스토리북 3종.
**테스트**: 키보드만으로 설문 완료, 새로고침 복구 스냅샷.

---

## Track C · Observability, Security & Ops

### Task C1 — X-Request-ID & OpenTelemetry hardening

기획: 로그 보존·접근 정책, request_id 재현 플로우.
개발: 미들웨어로 request_id 생성/응답, OTel 스팬에 속성 전파, 헤더 왕복·로그 상관 테스트.
DoD: 요청-로그-트레이스 ID 일치.

### Task C2 — Security headers & Cloudflare rollout

기획: noindex/no-store/CSP 정책, Cloudflare 운용값 기록.
개발: 엔드포인트별 헤더 적용, SSL/WAF/Rate-limit/Bot 설정 후 캡처 저장.
테스트: curl로 헤더 확인, WAF/Rate-limit 로깅.

### Task C3 — Decision packet & audit logging prep

기획: decision_packet 필드 정의, 감사 이벤트(`participant_submitted`, `aggregate_recomputed`).
개발: 로그/해시 저장, 커플 플로우와 호환성 확보.
DoD: 감사 로그 재현 가능, SRE 복구 절차 문서화.

---

## Track D · Testing & QA Enablement

### Task D1 — Participant flow test suite

기획: 테스트 플랜(등록/중복/프리뷰/k-lock/E2E), 브라우저 매트릭스.
개발: 단위/통합 + Playwright Self→Invite→3명 unlock, 무플레이크 3회 확인.

### Task D2 — Accessibility automation & manual checklist

기획: 수동 체크리스트(라벨/포커스/모달/대비), 대체 텍스트 문구.
개발: axe-core CLI CI 통합, 위반 0.

### Task D3 — Release gate verification

기획: Go/No-Go 항목(Web Vitals, noindex/CSP, PGI 스냅샷, OTel join, decision_packet hash).
개발: Lighthouse CI, 헤더 검사, problem+json 스키마 검사 자동화.

---

## Track E · Documentation & Coordination

### Task E1 — DeploymentPlan/Tickets/Runbook 업데이트

기획: 변경된 플로우/카피/테스트 반영.
개발: 티켓 상태, 테스트 로그, 스크린샷 연결.
DoD: 배포 문서에 헤더 캡처·Cloudflare 스냅샷·테스트 로그 포함.

### Task E2 — Cloudflare & 백업 전략 문서

기획: 정책 값/임계치·예외 대응 시나리오.
개발: 실제 설정 값, 검증 커맨드, 백업 빈도·복구 절차 기록.

### Task E3 — Couple-service alignment

기획: decision_packet 필드 합의, 의존성 표 정리.
개발: 이벤트 포맷/서명 규칙, 계약 테스트, 차기 스프린트 블로커 명시.

---

## Appendix A — API & Schema Quick Reference

```json
ParticipantRelation = ["friend","coworker","partner","family","other"]
```

```
POST /v1/participants/{token} → 201 { participant_id, relation, nickname }
POST /v1/answers/{participant_id} → 201 { saved: true }
GET  /v1/participants/{token}/preview → { respondent_count, locked, needed }
GET  /v1/report/{token} → 잠금 시 403 problem+json, 해금 시 radar/relations/pgi/confidence JSON
```

Problem+JSON 예시: `type,title,detail,status,instance,code` 필드 포함.

---

## Appendix B — Alembic rev.003 Checklist

- DDL 순서: 컬럼 추가 → 기본값/백필 → 제약 추가 → 인덱스.
- 다운그레이드: 제약 해제 → 컬럼 드롭.
- 페이지네이션 백필(대규모 DB), 롤백 시 기존 플로우 영향 검토.
- 프리/포스트 마이그레이션 읽기 호환 점검.
- 백필 로깅 및 계측.

---

## Appendix C — Security Headers & Cloudflare Targets

- 민감 HTML: `X-Robots-Tag: noindex, nofollow`, `Cache-Control: private, no-store`.
- OG PNG: `Cache-Control: public, max-age=600`, `ETag` 발급.
- CSP 기본: `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'`.
- Cloudflare 권장 설정: SSL Full(Strict), Rate-limit `/v1/invites` 60/min/IP, `/v1/answers` 120/min/IP, Bot JS Challenge.

---

## Appendix D — Representative Test Matrix

- **Unit**: enum 검증, 32문항 길이/범위, PGI 계산, 캐시 무효화.
- **Integration**: participants→answers→preview/report 연계.
- **E2E**: OwnerProfile→Invite→3명 참여→unlock, k=0/1/2 잠금 유지, 미리보기 장애 처리, 공개 페이지 개발 용어 0건 검사.
- **Accessibility**: 라벨, 포커스, 대비, 키보드 라디오 조작.

---

## 역할별 즉시 착수 항목
- **기획(PO/UX/카피)**: 라벨/카피·UX 결정을 문서화, 에러 카피 톤 확정.
- **백엔드**: Alembic rev.003, `/v1/participants|answers`, 집계 서비스/캐시.
- **프런트엔드**: OwnerProfile/인테이크/32문항/프리뷰 연결 및 카피 스냅샷.
- **DevOps**: Canonical/ALLOWED_HOSTS/헤더/Cloudflare 설정 검증·캡처.
- **QA**: D1~D3 테스트 스위트 구축, axe/Lighthouse CI 연동.

