# Self/Other 스키마 & 트랜잭션 플로우 설계

## 1. 개요

Self→Invite→Other→Aggregate 흐름을 정규화하면서 `sessions`-`participants`-`participant_answers`-`relation_aggregates`를 기준 도메인으로 정의한다. 모든 데이터 쓰기는 단일 SQLAlchemy 세션 트랜잭션에서 처리하고, 실패 시 전체 롤백을 강제해 응답/집계 불일치를 방지한다.

## 2. 엔터티 확장 요약

| 테이블 | 핵심 필드 | 목적 |
| ------ | --------- | ---- |
| `sessions` | `self_mbti`, `snapshot_owner_name`, `snapshot_owner_avatar` | Self 검사 결과 & 공유 용 카피 프리셋 |
| `participants` | `relation`, `display_name`, `consent_display`, `perceived_type`, `axes_payload` | 수신자 메타데이터 + 계산 캐시 |
| `participant_answers` | `participant_id`, `question_id`, `value` | 제3자 문항 원본 저장 |
| `relation_aggregates` | `respondent_count`, `top_type`, `consensus`, `pgi`, `axes_payload` | 관계별 집계/가이드 표현 |
| `responses_other.participant_id` | FK → `participants.id` | 레거시 경로 호환 (이관 단계) |

`participantrelation` ENUM(`friend`,`coworker`,`family`,`partner`,`other`)은 모든 테이블에서 동일하게 사용한다.

## 3. 트랜잭션 플로우

### 3.1 Self 결과 저장 (`POST /v1/self/mbti`)
1. 세션 조회 + 만료 검증.
2. `Session.self_mbti`, `snapshot_owner_*` 업데이트.
3. Self 문항 재제출 시 `responses_self` 전체 삭제 후 새 레코드 삽입.
4. `Aggregate` 즉시 재계산 → `axes_payload`를 사용하지 않지만, 향후 `relation_aggregates` 계산을 트리거하기 위해 워커 큐에 세션 ID enqueue.
5. 커밋 성공 시까지 트랜잭션 유지, 실패 시 롤백 + RFC 9457 ProblemDetails 반환.

### 3.2 초대 생성 (`POST /v1/invites`)
1. 세션 유효성 검증.
2. `participants`에 `(session_id, invite_token, relation='friend', consent_display=False)` 초기 레코드 생성 (relation은 수정 가능).
3. 커밋 후, 공유 URL(`/i/{token}`) 발행.

### 3.3 수신자 등록 (`POST /v1/participants/{token}`)
1. 토큰으로 `Participant` 조회 (행 잠금 `SELECT ... FOR UPDATE`).
2. 유효한 상태인지 검증 (만료, max_raters, 중복 등).
3. `relation`, `display_name`, `consent_display` 업데이트.
4. 커밋.

### 3.4 답변 제출 (`POST /v1/answers/{participant_id}`)
1. `Participant` 조회 + 세션 만료 검증.
2. 32문항 검증 (`questions_for_mode`).
3. 트랜잭션 내에서 `participant_answers` upsert:
   - 기존 레코드 삭제(`DELETE ... WHERE participant_id = :id`).
   - 새 레코드 배치 삽입.
4. `core_scoring.compute_type` 호출로 `(perceived_type, axes_payload)` 산출.
5. `participants` 행 업데이트 (`perceived_type`, `axes_payload`, `answers_submitted_at`, `computed_at`).
6. `relation_aggregates` 업데이트 큐 enqueue (비동기) 또는 즉시 리컴퓨트.
7. 커밋.

### 3.5 개인 미리보기 (`GET /v1/report/participant/{participant_id}`)
1. `Session.self_mbti` + `Participant.perceived_type` 로드.
2. `axes_payload` 사용해 축별 차이 벡터 생성.
3. 응답 전용 캐시는 존재하지만, 누락 시 404 대신 409(`answers-missing`).

### 3.6 집계 리포트 (`GET /v1/report/session/{session_id}`)
1. `relation_aggregates`에서 관계별 카드 가져오기.
2. `respondent_count >= 3` 인 관계만 공개. 전체 응답이 3 미만이면 `unlocked=False`.
3. `axes_payload`와 `pgi` 기반으로 커뮤니케이션 팁을 선택.

## 4. 롤백 시나리오 표

| 경로 | 실패 지점 | 롤백 동작 | 사용자 피드백 |
| ---- | --------- | ---------- | --------------- |
| Self 제출 | `recalculate_aggregate`에서 ScoringError | 세션 트랜잭션 롤백, 응답 저장 없음 | 400 `scoring-error` |
| Participant 등록 | 중복 토큰/락 타임아웃 | 트랜잭션 롤백, 기존 값 유지 | 409 `participant-locked` |
| 답변 제출 | 문항 검증 실패 | `participant_answers` 변경 없음 | 400 `answers-invalid` |
| 답변 제출 | DB write 예외 | 전 레코드 삭제도 롤백 | 500 `server-error` |
| 집계 워커 | concurrency update conflict | 워커 트랜잭션 롤백 후 재시도 | 내부 재시도 |

## 5. `core_scoring` 연동 체크리스트

- `participants.axes_payload`는 `{"ei":-0.42, "sn":0.17, "tf":-0.13, "jp":0.58}` 형태로 저장.
- `participants.perceived_type`는 16 MBTI 유형 중 하나. 계산 시 비표준 조합 발생 시 ValidationError → 트랜잭션 롤백.
- 집계는 `relation_aggregates.axes_payload`에 평균 벡터를, `consensus`에는 최빈 유형 비율을 저장.

## 6. 데이터 마이그레이션 노트

- 기존 `responses_other`는 `participant_id`를 NULL로 유지 (백필 워커 필요).
- 위 기능 완성 전까지는 레거시 라우터가 `rater_hash` 기반으로 계속 작동하므로, 새 라우터는 `participant_answers` 사용하도록 별도 네임스페이스(`/v1/`)에 둔다.
- 마이그레이션 실행 순서: `002` → `003_self_other_schema` → 이후 백필 스크립트.

## 7. 모니터링/테스트 포인트

- Alembic head 상태 확인: `alembic history --verbose`.
- 단위 테스트: `pytest tests/test_participant_flow.py::test_compute_type_valid` (추가 예정).
- 테스트 픽스처: `testing_utils.build_fake_answers()` 활용해 일관된 제3자 응답 세트 구성.
- 계약 테스트: `testing_utils/fixtures/participant_preview.json` + 스냅샷 비교.
