"""Couple scoring helpers shared by API workers and background jobs.

The module keeps pure computations isolated from persistence so that
FastAPI handlers, Celery tasks, or offline scripts can import the same
logic.  All helpers operate on in-memory dictionaries to make unit
testing straightforward and to support deterministic decision packets.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Dict, Iterable, List, Sequence


# === Questionnaire metadata ==================================================
# Each scale groups the Likert items that should be averaged together.
SCALES: dict[str, list[str]] = {
    "CS": ["CS1", "CS2", "CS3", "CS4", "CS5", "CS6"],  # Communication Safety
    "EA": ["EA1", "EA2", "EA3", "EA4", "EA5", "EA6"],  # Emotional Awareness
    "CB": ["CB1", "CB2", "CB3", "CB4", "CB5", "CB6"],  # Cognitive Bias
    "PD": ["PD1", "PD2", "PD3", "PD4", "PD5", "PD6"],  # Pursue / Distance
    "RP": ["RP1", "RP2", "RP3", "RP4", "RP5", "RP6"],  # Relationship Planning
    "LF": ["LF1", "LF2", "LF3", "LF4", "LF5", "LF6"],  # Lifestyle Fit
    "IN": ["IN1", "IN2", "IN3", "IN4", "IN5", "IN6"],  # Intimacy / Needs
    "SF": ["SF1", "SF2", "SF3", "SF4", "SF5", "SF6"],  # Shared Future
}

# Reverse coded items – scored as 4 - value.
REV_ITEMS: set[str] = {
    "CS2",
    "CB1",
    "CB2",
    "CB3",
    "CB4",
    "PD5",
    "PD6",
    "LF2",
    "LF5",
    "IN4",
    "SF3",
    "SF6",
}

# Pre-compute question -> scale membership for quick validation.
QUESTION_TO_SCALE: dict[str, str] = {
    code: scale for scale, codes in SCALES.items() for code in codes
}

# === Exceptions ==============================================================


class ScoringValidationError(ValueError):
    """Raised when the provided answers cannot be processed safely."""


class MissingResponsesError(ScoringValidationError):
    """Raised when an answer set is incomplete for the required scales."""


# === Core helpers ============================================================


def score_item(code: str, value: int) -> float:
    """Return the normalized value for a single item.

    The questionnaire uses a 0–4 scale.  Reverse-coded items are
    mirrored to keep higher values representing stronger agreement with
    the positive pole.
    """

    if value is None:
        raise ScoringValidationError(f"value is required for item {code}")
    upper_bound = 10 if code == "SF1" else 4
    if value < 0 or value > upper_bound:
        raise ScoringValidationError(
            f"value for {code} must be within 0..{upper_bound}, received {value}"
        )
    if code in REV_ITEMS:
        return float(4 - value)
    if code == "SF1":
        # SF1는 0–10 점수를 0–4 척도로 정규화한다.
        return float(value) * 0.4
    return float(value)


def scale_mean(codes: Sequence[str], answers: Dict[str, int]) -> float:
    """Average a collection of item codes, raising if any are missing."""

    values: list[float] = []
    missing: list[str] = []
    for code in codes:
        if code not in answers:
            missing.append(code)
            continue
        values.append(score_item(code, answers[code]))

    if missing:
        raise MissingResponsesError(
            "missing responses for items: " + ", ".join(sorted(missing))
        )

    if not values:
        raise ScoringValidationError("no values supplied for scale computation")

    return sum(values) / len(values)


def compute_scale_means(answers: Dict[str, int]) -> Dict[str, float]:
    """Compute average scores for each scale from the raw answers."""

    return {scale: scale_mean(codes, answers) for scale, codes in SCALES.items()}


@dataclass(frozen=True)
class DeltaBundle:
    delta_items_a: Dict[str, float]
    delta_items_b: Dict[str, float]
    delta_scales_a: Dict[str, float]
    delta_scales_b: Dict[str, float]


def compute_deltas(
    answers_a_self: Dict[str, int],
    answers_a_guess: Dict[str, int],
    answers_b_self: Dict[str, int],
    answers_b_guess: Dict[str, int],
) -> DeltaBundle:
    """Return absolute deltas per item and averaged per scale for both partners."""

    # Item-level deltas (absolute difference between guess and the other person's self).
    delta_items_a = {
        code: abs(float(answers_a_guess.get(code, 0)) - float(answers_b_self.get(code, 0)))
        for code in QUESTION_TO_SCALE
        if code in answers_a_guess and code in answers_b_self
    }
    delta_items_b = {
        code: abs(float(answers_b_guess.get(code, 0)) - float(answers_a_self.get(code, 0)))
        for code in QUESTION_TO_SCALE
        if code in answers_b_guess and code in answers_a_self
    }

    def scale_delta(delta_items: Dict[str, float]) -> Dict[str, float]:
        per_scale: dict[str, list[float]] = {scale: [] for scale in SCALES}
        for code, value in delta_items.items():
            scale = QUESTION_TO_SCALE[code]
            per_scale[scale].append(value)
        return {
            scale: (sum(values) / len(values)) if values else 0.0
            for scale, values in per_scale.items()
        }

    return DeltaBundle(
        delta_items_a=delta_items_a,
        delta_items_b=delta_items_b,
        delta_scales_a=scale_delta(delta_items_a),
        delta_scales_b=scale_delta(delta_items_b),
    )


def rank_top_delta_items(
    deltas_a: Dict[str, float],
    deltas_b: Dict[str, float],
    *,
    limit: int = 5,
) -> list[str]:
    """Select the item codes with the largest combined delta."""

    combined: dict[str, float] = {}
    for code, value in deltas_a.items():
        combined[code] = value
    for code, value in deltas_b.items():
        combined[code] = max(combined.get(code, 0.0), value)

    ordered = sorted(combined.items(), key=lambda item: item[1], reverse=True)
    return [code for code, _ in ordered[:limit]]


# === Flagging and insights ===================================================

FLAG_SEVERITY = {"info", "low", "mid", "high"}


def flag_rules(scales: Dict[str, float], raw_self: Dict[str, int]) -> list[dict[str, str]]:
    """Derive qualitative flags using heuristics from the PRD."""

    flags: list[dict[str, str]] = []

    def add(code: str, severity: str, reason: str) -> None:
        if severity not in FLAG_SEVERITY:
            raise ScoringValidationError(f"unsupported severity '{severity}'")
        flags.append({"code": code, "severity": severity, "reason": reason})

    # Safety / respect guardrails.
    if raw_self.get("CS2", 5) <= 2 or raw_self.get("IN4", 5) <= 2:
        add("SAFETY", "high", "존중/거절 신호가 낮음")

    # Pursue / withdraw high tension.
    if raw_self.get("PD1", 0) >= 3 and raw_self.get("PD3", 0) >= 3:
        add("PURSUIT_WITHDRAW", "mid", "추궁–회피 패턴 강도 높음")

    # Cognitive distortion accumulation.
    bias_count = sum(int(raw_self.get(code, 0) >= 3) for code in ["CB1", "CB2", "CB3", "CB4"])
    if bias_count >= 2:
        add("COGNITIVE", "mid", "흑백 사고 경향이 다수 문항에서 관측")

    # Planning misalignment on RP scale.
    if scales.get("RP", 0.0) <= 1.6:
        add("PLANNING_GAP", "low", "장기 계획에 대한 만족도가 낮음")

    return flags


INSIGHT_LIBRARY: dict[str, dict[str, str]] = {
    "CS": {
        "title": "대화 안전장치 점검",
        "summary": "말을 꺼내기 전 합의한 멈춤 규칙과 확인 질문으로 안전감을 높입니다.",
        "action": "서로 거절 신호를 들었을 때 사용할 '3초 숨 고르기'를 연습하세요.",
    },
    "EA": {
        "title": "감정 라벨 매칭",
        "summary": "감정을 수치화해 공유하면 상대가 추측에 의존하지 않아도 됩니다.",
        "action": "매일 밤 서로의 에너지/기분 점수를 0–4로 공유해 보세요.",
    },
    "CB": {
        "title": "생각 점검 루틴",
        "summary": "가정법이나 흑백 사고를 발견하면 사실 질문으로 전환합니다.",
        "action": "대화 중 '내가 단정한 부분이 있을까?'를 서로에게 묻는 신호를 정하세요.",
    },
    "PD": {
        "title": "추궁–회피 탈출구",
        "summary": "타임아웃과 재시작 시간 약속이 서로를 쫓고 숨는 패턴을 줄입니다.",
        "action": "20분 타임아웃 시 사용 가능한 대체 행동 3가지를 적어 공유하세요.",
    },
    "RP": {
        "title": "계획 vs 유연성 균형",
        "summary": "이정표를 미리 합의하되 즉흥 제스처를 위한 ‘열린 창’도 설계합니다.",
        "action": "다가올 한 달의 필수 일정과 깜짝 이벤트 여유 슬롯을 함께 채워보세요.",
    },
    "LF": {
        "title": "생활 리듬 조율",
        "summary": "휴식/집안일/여가 비중을 수치로 비교해 격차를 드러냅니다.",
        "action": "각자 이상적인 주간 일정(0-4 척도)을 작성하고 겹치는 부분을 찾으세요.",
    },
    "IN": {
        "title": "욕구 명료화",
        "summary": "감정적·신체적 친밀감을 요청하는 방식을 명확히 합의합니다.",
        "action": "서로가 선호하는 돌봄 행동 3가지를 적고, 기대 시점을 함께 정하세요.",
    },
    "SF": {
        "title": "공동 미래 시나리오",
        "summary": "같은 장면을 그릴수록 장기적 의사결정이 쉬워집니다.",
        "action": "3년 뒤 이상적인 하루를 스토리보드로 나누어 공유하세요.",
    },
}


def build_insights(
    delta_scales_a: Dict[str, float],
    delta_scales_b: Dict[str, float],
    flags: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Pick the top 3 insight cards based on deltas and flags."""

    # Prioritise any high severity flags at the top.
    ordered: list[dict[str, str]] = []
    severe = [flag for flag in flags if flag["severity"] == "high"]
    for flag in severe:
        ordered.append(
            {
                "type": "flag",
                "code": flag["code"],
                "title": "안전 경보",
                "summary": flag["reason"],
                "action": "대화 전에 안전 약속을 재확인하고 필요 시 전문가 도움을 요청하세요.",
            }
        )

    # Combine deltas per scale using the maximum partner delta.
    combined: dict[str, float] = {}
    for scale in SCALES:
        combined[scale] = max(delta_scales_a.get(scale, 0.0), delta_scales_b.get(scale, 0.0))

    scale_order = sorted(combined.items(), key=lambda item: item[1], reverse=True)

    for scale, value in scale_order:
        if scale not in INSIGHT_LIBRARY:
            continue
        card = INSIGHT_LIBRARY[scale]
        ordered.append(
            {
                "type": "scale",
                "scale": scale,
                "score": round(value, 3),
                "title": card["title"],
                "summary": card["summary"],
                "action": card["action"],
            }
        )

    # Return up to 3 insights.
    return ordered[:3]


# === Gap ratings =============================================================


def gap_grade(delta_value: float) -> str:
    """Translate a delta magnitude into qualitative labels."""

    if delta_value < 0.8:
        return "green"
    if delta_value < 1.6:
        return "amber"
    return "red"


def summarize_gap(delta_scales_a: Dict[str, float], delta_scales_b: Dict[str, float]) -> dict:
    """Return aggregate statistics (mean delta, largest scale, etc.)."""

    merged = [
        max(delta_scales_a.get(scale, 0.0), delta_scales_b.get(scale, 0.0))
        for scale in SCALES
    ]
    mean_delta = fmean(merged) if merged else 0.0
    scale_names = list(SCALES.keys())
    top_scale, top_value = max(
        ((scale, value) for scale, value in zip(scale_names, merged)),
        key=lambda item: item[1],
        default=(None, 0.0),
    )
    return {
        "mean_delta": round(mean_delta, 4),
        "top_scale": top_scale,
        "top_delta": round(top_value, 4),
        "grade": gap_grade(mean_delta),
    }


__all__ = [
    "SCALES",
    "REV_ITEMS",
    "ScoringValidationError",
    "MissingResponsesError",
    "score_item",
    "scale_mean",
    "compute_scale_means",
    "compute_deltas",
    "DeltaBundle",
    "rank_top_delta_items",
    "flag_rules",
    "build_insights",
    "gap_grade",
    "summarize_gap",
]
