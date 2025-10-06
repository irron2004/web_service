# 관계별 평가 모듈 요약

본 문서는 친구·직장·연인·가족 네 가지 외부 평가 모듈의 산출물을 한곳에 정리해 설문, 감사 스크립트, 리포트 템플릿을 빠르게 찾을 수 있게 돕습니다.

## 공통 규칙
- 리커트 1–5 (1=전혀 아니다, 5=매우 그렇다), 스코어링은 `(응답값-3) * sign`.
- 차원별 문항 수는 12개(총 48개)이며, E/S/T/J는 순방향, I/N/F/P는 역채점입니다.
- 모듈별 JSON은 `docs/questionnaire.v1.json`의 `questions` 섹션에 위치하며, 감사 스크립트는 `scripts/` 디렉터리에 있습니다.
- 리포트 템플릿(YAML)은 `docs/` 루트에 존재하며 Jinja2 규칙을 따른 문구 템플릿입니다.

## 친구 모듈 (Friend)
- 문항: `docs/questionnaire.v1.json` → `questions.modes.friend` (ID `F-EI-01`~`F-JP-12`).
- 역채점: I/N/F/P 극성 24문항 (50%).
- 감사 스크립트: `scripts/audit_friend_module.py` (`python scripts/audit_friend_module.py --path friend.json`).
- 리포트 템플릿: `docs/friend_report_template.yaml` (Self vs 친구 TL;DR + 축별 인사이트).

## 직장 모듈 (Work)
- 문항: `docs/questionnaire.v1.json` → `questions.modes.work` (ID `W-EI-01`~`W-JP-12`).
- 역채점: I/N/F/P 극성 24문항 (50%).
- 감사 스크립트: `scripts/audit_work_module.py` (`--path work.json` 또는 `RAW_JSON`).
- 리포트 템플릿: `docs/work_report_template.yaml` (업무 협업 톤).

## 연인 모듈 (Partner)
- 문항: `docs/questionnaire.v1.json` → `questions.modes.partner` (ID `P-EI-01`~`P-JP-12`).
- 역채점: I/N/F/P 극성 24문항 (50%).
- 감사 스크립트: `scripts/audit_partner_module.py`.
- 리포트 템플릿: `docs/partner_report_template.yaml` (warm-empathetic 톤).

## 가족 모듈 (Family)
- 문항: `docs/questionnaire.v1.json` → `questions.modes.family` (ID `G-EI-01`~`G-JP-12`).
- 역채점: I/N/F/P 극성 24문항 (50%).
- 감사 스크립트: `scripts/audit_family_module.py`.
- 리포트 템플릿: `docs/family_report_template.yaml` (respectful-warm 톤).

## 활용 메모
- 설문 생성기는 `questions.modes.<relation>` 배열을 순회해 Self/Other 문구를 각각 렌더링합니다.
- 감사 스크립트를 사용하면 JSON 초안에서도 역채점 비율, 차원 분포, sign 일관성을 즉시 확인할 수 있습니다.
- 리포트 템플릿은 PGI, 축 차이, axis_shift 값을 주입해 TL;DR + 제안 문장을 자동 생성하도록 설계되었습니다.
