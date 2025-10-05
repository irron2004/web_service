# Viral Intake Feedback TODOs

## Immediate Fixes (48h)
- [x] Remove mandatory email collection from `/mbti/friend` and `/mbti/share`; collect only display name (optional) and relationship tag per PRD.
- [x] Strip developer-facing copy (e.g., RFC 9457, X-Request-ID, OpenTelemetry, `noindex`) from public pages; replace with user-friendly messaging outlined in feedback.
- [x] Introduce respondent intake on `/mbti/friend` with required relationship selection (친구/가족/부부/직장/기타) and optional display name with anonymous fallback before survey questions.
- [ ] Create dedicated owner profile flow: collect owner display name, avatar, and MBTI → generate `/i/{token}` invite with owner identity surfaced in header.
- [x] Hide unfinished Arcade/Statistics navigation entries until backed by live pages or feature flags.
- [ ] Upgrade self-test UX: remove internal documentation references, ensure accessible radio controls, add progress indicator and completion CTA that stores self type and advances to invite creation.

## Follow-up Items (Next Sprint)
- [ ] Enforce k≥3 gating in code (not just copy), add OG metadata, confirm `noindex` and CSP headers, and surface session snapshot fields for consistent display names.
- [ ] Wire preview/result APIs with error fail-safes and observability hooks (X-Request-ID propagation, OpenTelemetry spans) per tickets TKT-009~013.
- [ ] Update deployment/security documentation after implementing the above (e.g., DeploymentPlan, Tickets status).

## Copy Updates Needed
- [x] `/mbti/friend`: Replace technical copy with guidance on choosing relationship, optional nickname, anonymity, and k≥3 insight unlock condition.
- [x] `/mbti/friend-system`: Update evaluation steps to emphasize display name + relationship selection, 24~32 question flow, and link-only sharing (email optional/omitted).
- [x] `/mbti/self-test`: Replace reference text with user instruction: "느낌에 가까운 쪽을 선택해 주세요. 키보드만으로도 응답할 수 있어요."

## Validation/Testing Checklist
- [ ] Verify `/mbti/friend` loads without server errors post-update and routes respondents through new intake before the survey.
- [ ] Confirm owner profile completion gates invite generation and that `/i/{token}` headers show owner display name/avatar.
- [ ] Ensure hidden menu items no longer appear in navigation, and all visible links resolve (no 404s).
- [ ] Regression test invite/share flows to confirm privacy requirements and analytics hooks remain intact.
