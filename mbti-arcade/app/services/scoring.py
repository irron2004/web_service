from __future__ import annotations

from statistics import fmean
from typing import Dict, Iterable, List

from app.schemas import DIMENSIONS

RELATION_WEIGHTS = {
    None: 1.0,
    "friend": 1.0,
    "core_friend": 1.2,
    "partner": 1.5,
    "couple": 1.5,
    "family": 1.1,
    "coworker": 1.1,
}


class ScoringError(ValueError):
    pass


def compute_norms(
    answers: Iterable[tuple[int, int]], question_lookup: Dict[int, tuple[str, int]]
) -> Dict[str, float]:
    totals: Dict[str, float] = {dim: 0.0 for dim in DIMENSIONS}
    counts: Dict[str, int] = {dim: 0 for dim in DIMENSIONS}

    for question_id, value in answers:
        if question_id not in question_lookup:
            raise ScoringError(f"Unknown question_id={question_id}")
        if value < 1 or value > 5:
            raise ScoringError(f"Answer value must be 1..5 (question_id={question_id})")
        dim, sign = question_lookup[question_id]
        delta = value - 3
        totals[dim] += sign * delta
        counts[dim] += 1

    norms: Dict[str, float] = {}
    for dim in DIMENSIONS:
        if counts[dim] == 0:
            raise ScoringError(f"Missing answers for dimension {dim}")
        norms[dim] = totals[dim] / (2 * counts[dim])
    return norms


def norm_to_radar(norms: Dict[str, float]) -> Dict[str, float]:
    return {dim: round((value + 1) * 50, 3) for dim, value in norms.items()}


def weight_for_relation(tag: str | None) -> float:
    normalized = tag.lower() if tag else None
    return RELATION_WEIGHTS.get(normalized, 1.0)


def weighted_mean(values: List[float], weights: List[float]) -> float:
    numerator = sum(v * w for v, w in zip(values, weights))
    denominator = sum(weights)
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def weighted_sigma(values: List[float], weights: List[float]) -> float:
    mean = weighted_mean(values, weights)
    numerator = sum(w * (v - mean) ** 2 for v, w in zip(values, weights))
    denominator = sum(weights)
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) ** 0.5


def compute_gap_metrics(
    self_norm: Dict[str, float],
    other_norms: List[Dict[str, float]],
    weights: List[float],
) -> tuple[Dict[str, float], Dict[str, float], Dict[str, float], float]:
    if not other_norms or not weights:
        raise ScoringError("Other norms required")

    agg_other: Dict[str, float] = {}
    sigma: Dict[str, float] = {}
    gaps: Dict[str, float] = {}

    for dim in DIMENSIONS:
        values = [norm[dim] for norm in other_norms]
        dim_mean = weighted_mean(values, weights)
        agg_other[dim] = dim_mean
        sigma[dim] = weighted_sigma(values, weights)
        gaps[dim] = dim_mean - self_norm[dim]

    gap_score = fmean(abs(gaps[dim]) for dim in DIMENSIONS) * 100
    return agg_other, sigma, gaps, gap_score
