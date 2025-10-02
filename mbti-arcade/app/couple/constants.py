"""Static metadata for the couple perception gap questionnaire.

The prompts are intentionally concise so the backend can expose them to
clients if needed without depending on an external CMS.  Designers may
swap the copy later; the backend only relies on the code, scale, and
reverse-coded flags defined in :mod:`app.core_scoring`.
"""

from __future__ import annotations

from typing import Dict

from app.core_scoring import QUESTION_TO_SCALE

# Human friendly metadata keyed by item code.  Each entry describes the
# short prompt and the conversational theme.  This doubles as a source
# of truth for validation when sessions are restored after a refresh.
QUESTION_REGISTRY: Dict[str, dict[str, str]] = {
    "CS1": {
        "prompt_self": "나는 갈등을 말로 풀기 전에 분위기를 안정시키는 편이다.",
        "prompt_guess": "파트너는 갈등을 말로 풀기 전에 분위기를 안정시킨다.",
        "theme": "conversation_ground_rule",
    },
    "CS2": {
        "prompt_self": "나는 거절을 말했을 때 상대가 실망해도 안전하다고 느낀다.",
        "prompt_guess": "파트너는 거절을 말했을 때도 안전하다고 느낀다.",
        "theme": "safety_boundary",
    },
    "CS3": {
        "prompt_self": "나는 힘든 이야기를 해도 상대가 끼어들지 않고 들어준다.",
        "prompt_guess": "파트너는 힘든 이야기를 해도 내가 끼어들지 않는다고 느낀다.",
        "theme": "listening",
    },
    "CS4": {
        "prompt_self": "나는 감정이 격해지면 타임아웃을 먼저 제안한다.",
        "prompt_guess": "파트너는 감정이 격해지면 타임아웃을 먼저 제안한다.",
        "theme": "timeout",
    },
    "CS5": {
        "prompt_self": "나는 대화 전 목표를 확인하며 같은 방향을 맞춘다.",
        "prompt_guess": "파트너는 대화 전 목표를 확인하려 한다.",
        "theme": "alignment",
    },
    "CS6": {
        "prompt_self": "나는 대화 중 감정 지표(0-4)를 공유한다.",
        "prompt_guess": "파트너는 대화 중 감정 지표를 알려준다.",
        "theme": "emotional_barometer",
    },
    "EA1": {
        "prompt_self": "나는 내 감정 변화를 0-4 점수로 표현한다.",
        "prompt_guess": "파트너는 자신의 감정을 점수로 표현한다.",
        "theme": "emotion_label",
    },
    "EA2": {
        "prompt_self": "나는 파트너의 감정을 이름 붙여 확인한다.",
        "prompt_guess": "파트너는 내 감정을 이름 붙여 확인한다.",
        "theme": "mirroring",
    },
    "EA3": {
        "prompt_self": "나는 감정이 격할 때 숨 고르기 루틴을 사용한다.",
        "prompt_guess": "파트너는 감정이 격할 때 숨 고르기를 사용한다.",
        "theme": "regulation",
    },
    "EA4": {
        "prompt_self": "나는 감정 일지를 쓰며 패턴을 되돌아본다.",
        "prompt_guess": "파트너는 감정 일지를 써서 되돌아본다.",
        "theme": "reflection",
    },
    "EA5": {
        "prompt_self": "나는 감정 단서를 몸의 감각으로 알아차린다.",
        "prompt_guess": "파트너는 감정 단서를 몸의 감각으로 알아차린다.",
        "theme": "somatic_awareness",
    },
    "EA6": {
        "prompt_self": "나는 감정을 말하기 전에 상대의 수용도를 묻는다.",
        "prompt_guess": "파트너는 감정을 말하기 전에 나의 수용도를 묻는다.",
        "theme": "consent_check",
    },
    "CB1": {
        "prompt_self": "나는 상황을 흑백으로 나누어 말하곤 한다.",
        "prompt_guess": "파트너는 상황을 흑백으로 나누어 말한다.",
        "theme": "black_and_white",
    },
    "CB2": {
        "prompt_self": "나는 상대가 내 마음을 읽어야 한다고 기대한다.",
        "prompt_guess": "파트너는 내가 마음을 읽어주길 기대한다.",
        "theme": "mind_reading",
    },
    "CB3": {
        "prompt_self": "나는 작은 신호를 근거로 결론을 내린다.",
        "prompt_guess": "파트너는 작은 신호를 근거로 결론을 내린다.",
        "theme": "jump_to_conclusion",
    },
    "CB4": {
        "prompt_self": "나는 논의를 승패로 인식할 때가 있다.",
        "prompt_guess": "파트너는 논의를 승패로 인식한다.",
        "theme": "win_lose",
    },
    "CB5": {
        "prompt_self": "나는 의심이 들면 근거를 찾아보고 싶어한다.",
        "prompt_guess": "파트너는 의심이 들면 근거를 찾아본다.",
        "theme": "fact_check",
    },
    "CB6": {
        "prompt_self": "나는 통계나 데이터를 근거로 삼는다.",
        "prompt_guess": "파트너는 데이터를 근거로 삼는다.",
        "theme": "evidence",
    },
    "PD1": {
        "prompt_self": "나는 대화에서 상대를 몰아붙이는 편이다.",
        "prompt_guess": "파트너는 대화에서 나를 몰아붙인다.",
        "theme": "pursue",
    },
    "PD2": {
        "prompt_self": "나는 갈등이 있으면 바로 해결하고 싶다.",
        "prompt_guess": "파트너는 갈등을 바로 해결하고 싶어한다.",
        "theme": "resolve_now",
    },
    "PD3": {
        "prompt_self": "나는 갈등 시 자리를 피하고 싶어진다.",
        "prompt_guess": "파트너는 갈등 시 자리를 피하고 싶어한다.",
        "theme": "withdraw",
    },
    "PD4": {
        "prompt_self": "나는 갈등 주제를 미루고 싶을 때가 많다.",
        "prompt_guess": "파트너는 갈등 주제를 미루려 한다.",
        "theme": "delay",
    },
    "PD5": {
        "prompt_self": "나는 갈등 중 상대의 말을 끊지 않으려 노력한다.",
        "prompt_guess": "파트너는 갈등 중 말을 끊지 않으려 한다.",
        "theme": "listening_effort",
    },
    "PD6": {
        "prompt_self": "나는 다시 이야기할 시간을 제안한다.",
        "prompt_guess": "파트너는 다시 이야기할 시간을 제안한다.",
        "theme": "reconnect_plan",
    },
    "RP1": {
        "prompt_self": "나는 관계의 주요 이벤트를 캘린더에 기록한다.",
        "prompt_guess": "파트너는 주요 이벤트를 캘린더에 기록한다.",
        "theme": "milestone_planning",
    },
    "RP2": {
        "prompt_self": "나는 재정/생활 계획을 정기적으로 점검한다.",
        "prompt_guess": "파트너는 재정/생활 계획을 점검한다.",
        "theme": "financial_sync",
    },
    "RP3": {
        "prompt_self": "나는 계획 변경 시 대안을 제시한다.",
        "prompt_guess": "파트너는 계획 변경 시 대안을 제시한다.",
        "theme": "contingency",
    },
    "RP4": {
        "prompt_self": "나는 주간 회의를 열어 집안일을 조율한다.",
        "prompt_guess": "파트너는 주간 회의로 집안일을 조율한다.",
        "theme": "household_cadence",
    },
    "RP5": {
        "prompt_self": "나는 깜짝 이벤트를 위해 일정 여유를 남겨둔다.",
        "prompt_guess": "파트너는 일정에 여유를 남겨둔다.",
        "theme": "surprise_slot",
    },
    "RP6": {
        "prompt_self": "나는 계획을 공유 문서로 관리한다.",
        "prompt_guess": "파트너는 계획을 공유 문서로 관리한다.",
        "theme": "shared_doc",
    },
    "LF1": {
        "prompt_self": "나는 휴식/업무/집안일 시간을 균형 있게 잡는다.",
        "prompt_guess": "파트너는 휴식/업무/집안일을 균형 있게 잡는다.",
        "theme": "lifestyle_balance",
    },
    "LF2": {
        "prompt_self": "나는 파트너의 일정에 맞춰 내 일정을 조정한다.",
        "prompt_guess": "파트너는 내 일정에 맞춰 자신의 일정을 조정한다.",
        "theme": "schedule_adjust",
    },
    "LF3": {
        "prompt_self": "나는 공동 취미 시간을 꾸준히 확보한다.",
        "prompt_guess": "파트너는 공동 취미 시간을 확보한다.",
        "theme": "shared_hobby",
    },
    "LF4": {
        "prompt_self": "나는 집안 역할 분담에 만족한다.",
        "prompt_guess": "파트너는 집안 역할 분담에 만족한다.",
        "theme": "domestic_fairness",
    },
    "LF5": {
        "prompt_self": "나는 일정 캘린더를 서로 공유한다.",
        "prompt_guess": "파트너는 일정 캘린더를 공유한다.",
        "theme": "calendar_sync",
    },
    "LF6": {
        "prompt_self": "나는 생활 패턴 변화 시 미리 이야기를 꺼낸다.",
        "prompt_guess": "파트너는 생활 패턴 변화를 미리 이야기한다.",
        "theme": "pattern_change",
    },
    "IN1": {
        "prompt_self": "나는 정서적 돌봄 방법을 명확히 요청한다.",
        "prompt_guess": "파트너는 돌봄을 명확히 요청한다.",
        "theme": "care_request",
    },
    "IN2": {
        "prompt_self": "나는 감정적 신호를 알아채면 바로 반응한다.",
        "prompt_guess": "파트너는 감정 신호에 바로 반응한다.",
        "theme": "attunement",
    },
    "IN3": {
        "prompt_self": "나는 신체적 친밀감의 경계를 공유한다.",
        "prompt_guess": "파트너는 신체적 경계를 공유한다.",
        "theme": "boundary",
    },
    "IN4": {
        "prompt_self": "나는 요청을 거절할 때도 안전하다고 느낀다.",
        "prompt_guess": "파트너는 요청을 거절해도 안전하다고 느낀다.",
        "theme": "consent",
    },
    "IN5": {
        "prompt_self": "나는 돌봄 행동에 대한 감사 표현을 자주 한다.",
        "prompt_guess": "파트너는 돌봄 행동에 감사 표현을 한다.",
        "theme": "gratitude",
    },
    "IN6": {
        "prompt_self": "나는 친밀 시간 이후 서로의 느낌을 체크한다.",
        "prompt_guess": "파트너는 친밀 시간 이후 느낌을 체크한다.",
        "theme": "aftercare",
    },
    "SF1": {
        "prompt_self": "나는 3년 뒤 우리의 모습을 구체적으로 그린다 (0-10).",
        "prompt_guess": "파트너는 3년 뒤 모습을 구체적으로 그린다.",
        "theme": "future_story",
    },
    "SF2": {
        "prompt_self": "나는 장기 목표를 점검하는 대화를 즐긴다.",
        "prompt_guess": "파트너는 장기 목표 점검 대화를 즐긴다.",
        "theme": "future_checkin",
    },
    "SF3": {
        "prompt_self": "나는 미래 시나리오에서 부정적 상상에 빠지곤 한다.",
        "prompt_guess": "파트너는 미래를 걱정하는 상상을 한다.",
        "theme": "catastrophizing",
    },
    "SF4": {
        "prompt_self": "나는 중요 결정을 내릴 때 공동 원칙을 확인한다.",
        "prompt_guess": "파트너는 중요 결정을 공동 원칙과 비교한다.",
        "theme": "decision_values",
    },
    "SF5": {
        "prompt_self": "나는 미래 계획 문서를 작성해 공유한다.",
        "prompt_guess": "파트너는 미래 계획을 문서로 공유한다.",
        "theme": "future_doc",
    },
    "SF6": {
        "prompt_self": "나는 미래를 이야기할 때 최악을 대비한다.",
        "prompt_guess": "파트너는 미래 이야기에서 최악을 대비한다.",
        "theme": "risk_planning",
    },
}

# Ensure we did not miss codes declared in core_scoring.
MISSING_FROM_REGISTRY = set(QUESTION_TO_SCALE) - set(QUESTION_REGISTRY)
if MISSING_FROM_REGISTRY:
    missing = ", ".join(sorted(MISSING_FROM_REGISTRY))
    raise RuntimeError(f"QUESTION_REGISTRY missing definitions for: {missing}")
