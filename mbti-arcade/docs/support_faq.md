# Couple Flow FAQ & Support Checklist

## 주요 문의 요약
- **안전 플래그가 떴어요**: 보고서 플래그 코드(`SAFETY`, `PURSUIT_WITHDRAW` 등)를 설명하고, 상담 연계가 아닌 자체 대화 가이드를 제공.
- **참여 링크가 잠겼습니다**: k<3 이거나 Stage1 미완료 시 결과가 잠금 상태로 유지된다는 점 안내, 추가 참여자를 어떻게 초대하는지 설명.
- **결정 패킷 재발급 요청**: `packet_sha256`을 기준으로 무결성을 확인하고, 필요 시 `report.generated` 이벤트 로그와 함께 새 PDF/JSON을 발급.

## 지원 체크리스트
1. 세션 ID, 참여자 역할 토큰을 확보한다.
2. `GET /api/couples/sessions/{id}`로 k-state(threshold/current/visible)와 stage가 기대와 일치하는지 확인.
3. `decision_packets`에서 `packet_sha256`을 조회해 최신 버전(`model_id`, `code_ref`)인지 검증.
4. 안전 플래그 문의 시, 플래그 코드별 설명 문구(문서 링크 포함)를 제공하고 AdSense/금지 사례 기준을 확인.
5. 재발급이 필요하면 보고서 렌더 파이프라인을 실행하고, `report.generated` AuditEvent가 기록됐는지 확인.
6. 이슈 재발 방지를 위해 `mbti-arcade/docs/agent_runbook.md` 롤백/알림 절차를 검토하고, 필요 시 버그 리포트를 생성한다.
