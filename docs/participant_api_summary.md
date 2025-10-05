# Participant API & Relation Aggregate Implementation Notes

## BE-Participant-API
- `/v1/participants/{invite_token}` 등록, `/v1/answers/{participant_id}` 제출, `/v1/participants/{invite_token}/preview` 미리보기 엔드포인트를 FastAPI 라우터에 추가했습니다. 초대 토큰 검증, 세션 활성화 확인, 참여자 한도 초과시 RFC 9457 ProblemDetails 오류를 반환합니다.【F:mbti-arcade/app/routers/participants.py†L38-L129】
- 응답 제출 시 기존 답변을 정리하고 `ParticipantAnswer`/`OtherResponse`를 재삽입하며, 축 점수와 MBTI 유형을 재계산한 뒤 종합 및 관계별 집계를 호출합니다. 응답자는 3명 이상일 때 공개되며 임계값도 응답으로 포함됩니다.【F:mbti-arcade/app/routers/participants.py†L169-L257】
- 프리뷰 엔드포인트는 관계별 집계 결과와 참여자 목록을 결합하고, 잠금 해제 여부에 따라 상세 지표(축 평균, 상위 유형, PGI 등)를 조건부로 노출합니다.【F:mbti-arcade/app/routers/participants.py†L259-L322】

## BE-Relation-Aggregate
- `recalculate_relation_aggregates`를 추가해 세션별 관계 묶음을 계산하고, 응답 수와 축 평균, 상위 유형 비율, 합의도(consensus), PGI를 저장합니다.【F:mbti-arcade/app/services/aggregator.py†L94-L203】
- 기존 종합 집계 로직은 유지하되 `RelationAggregate` ORM 레코드를 upsert하고, 테스트 안정성을 위해 관계별 결과를 정렬해 반환합니다.【F:mbti-arcade/app/services/aggregator.py†L204-L247】

## BE-Backfill-Worker
- `scripts/backfill_participants.py` 스크립트가 레거시 `OtherResponse`를 세션별로 그룹화해 `Participant`/`ParticipantAnswer` 레코드를 생성·동기화하고, 건마다 축 점수/MBTI를 재계산합니다.【F:mbti-arcade/scripts/backfill_participants.py†L1-L146】
- 드라이런 지원(`--dry-run`)과 요약 로그(`logs/backfill_participants.log`) 기록, 집계 재계산 호출을 통해 안전한 백필 수행 흐름을 제공합니다.【F:mbti-arcade/scripts/backfill_participants.py†L147-L209】

## QA-Contract-Tests
- `test_participant_flow.py`가 Self→Invite→Other→Preview 플로우를 시뮬레이션해 등록/제출, 중복 제출 덮어쓰기, 잠금 해제 전후 동작, RFC 9457 오류 응답을 검증합니다.【F:mbti-arcade/tests/integration/test_participant_flow.py†L1-L118】
- 공용 테스트 유틸에 결정적 답안 빌더와 프리뷰 스냅샷 픽스처를 추가해 계약 테스트의 안정성을 확보했습니다.【F:testing_utils/fixtures/__init__.py†L1-L23】【F:testing_utils/fixtures/participant_preview.json†L1-L25】

## Docs-Playbook-Update
- DeploymentPlan에 003 마이그레이션 적용·롤백 절차와 백필 워커 실행·검증 단계를 기록했습니다.【F:DeploymentPlan.md†L36-L71】
- 테스트 가이드에는 참가자 플로우 계약 테스트 실행 명령을 통합해 QA 체크리스트를 확장했습니다.【F:docs/testing.md†L15-L33】
