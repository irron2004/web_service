# 내가너라면 MBTI TODO

## 백엔드 / API
- (완료) RFC 9457 오류 응답과 k≥3 가드 검증을 포함해 `/api/self`, `/api/other`, `/api/result`, `/share` 플로우를 회귀 테스트로 고정하기 *(테스트 실행은 후속 일괄 수행 예정)*
- 집계/스코어링 서비스의 경계값·동시성 케이스 추가하고 worker 경고(시간 초과, 중복 집계) 모니터링 연결하기
- `/share/og/{token}.png` 렌더러 성능(<200ms)·캐시 정책(ETag, Cache-Control)·1200×630 규격을 점검하고 문서화하기
- 세션 만료(`compute_expiry`)·rate limit·k-익명 조건을 운영환경 설정과 일치시키기

## 관측 / 보안
- `configure_observability`에서 OTEL exporter 설정, X-Request-ID 전파, 문제 발생 시 로그→스팬 코릴레이션 절차 문서화
- 공유/결과/OG 경로에 `X-Robots-Tag=noindex`가 빠지지 않도록 미들웨어/테스트 강화
- Cloud Run/Cloudflare 배포시 `DeploymentPlan.md` 내 수집 파이프라인·알림 채널 업데이트

## 프런트엔드 / 성장
- Self/Other 32문항 폼 진행바, 초대 공유 링크, Radar/Scatter 차트의 UX·WCAG 2.2 AA 검증 및 문구 확정
- GA4 추천 이벤트·UTM 파이프라인 구현, AdSense 위치/정책 위반 점검 및 스크린샷 수집
- Web Vitals/Lighthouse CI와 연결해 TTFB, INP, CLS 목표치 모니터링 대시보드 구성

## QA / 문서
- `test_share_flow` 등 E2E 로그 정리 및 스냅샷화, RFC 9457 오류 타입 스냅샷 유지
- API 계약/가이드 문서에서 세션 단계(k 상태, rate limit)와 응답 예제를 최신화
- 운영 시나리오(만료 세션, rate limit 초과, OG 캐시 미스) 체크리스트 작성
- 회귀 테스트 스위트 실행은 다음 작업들과 묶어 한 번에 진행 예정
