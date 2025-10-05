# 커플 MBTI TODO

## 백엔드 / API
- `CoupleService` 전 흐름(create → stage1 → responses → compute) 엔드투엔드 테스트 보강 및 롤백 전략 문서화
- 응답 업서트 idempotency·역할 검증(토큰 재사용, 중복 제출)을 위한 DB 제약·RFC 9457 오류 응답 확정
- 결정 패킷 저장소(`decision_packets`) 구조와 `code_ref`/`model_id` 버전 관리 방안 정의
- `core_scoring` 델타·플래그 규칙을 PRD와 교차 검증하고 극단값/누락값 단위 테스트 추가

## 데이터 / 리포트
- `partner_report_template.yaml` 등 템플릿을 실제 API 출력과 동기화하고 PDF/JSON 배포 경로 설계
- k-threshold 변경, stageVisible 전환, 결과 잠금 상태를 저장/조회 API에서 일관되게 노출하도록 스키마 점검
- 감사 로그(`AuditEvent`)에 주요 이벤트(session.created, responses.upserted, result.computed) 필수 필드 정의

## 프런트엔드 / UX
- 세션 생성 및 Stage1 K 상태 관리 UI, 각 파트너 응답 포털(토큰 로그인, 진행 안내) 설계·구현
- 결과 리포트 화면에 플래그·인사이트·상위 델타 항목을 시각화하고 안내 카피 확정
- 이메일/메신저 공유용 안내 템플릿과 Onboarding 튜토리얼 작성

## 관측 / 운영
- 커플 API 전 경로에 X-Request-ID·OTEL 스팬·KPI 메트릭(exporter) 연동 및 알림 룰 생성
- Stage3 완료, k>=threshold 전환, Rate-limit 초과 등 임계 이벤트에 대한 Slack/메일 알람 시나리오 정의
- 배포 시 롤백 플랜(Blue-Green, 데이터 마이그레이션)과 주 1회 스모크 테스트 일정 수립

## QA / 문서
- `test_couple_flow` 기반으로 실패 시나리오(역할 불일치, k 미충족, 허용 범위 외 stage) 케이스 추가
- API 문서에 토큰 교환, 단계별 상태 변화, RFC 9457 오류 타입(`/stage-incomplete`, `/question-invalid`) 명세
- 고객지원용 FAQ/진단 체크리스트(안전 플래그, 결정 패킷 재발급) 작성
