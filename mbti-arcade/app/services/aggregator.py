from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from sqlalchemy.orm import Session

from app.models import Aggregate, OtherResponse, Question, SelfResponse, Session as SessionModel
from app.services.scoring import (
    ScoringError,
    compute_gap_metrics,
    compute_norms,
    norm_to_radar,
    weight_for_relation,
)


class AggregateResult:
    def __init__(
        self,
        session_id: str,
        mode: str,
        self_norm: Dict[str, float],
        radar_self: Dict[str, float],
        other_norm: Dict[str, float] | None,
        radar_other: Dict[str, float] | None,
        gap: Dict[str, float] | None,
        sigma: Dict[str, float] | None,
        n: int,
        gap_score: float | None,
    ) -> None:
        self.session_id = session_id
        self.mode = mode
        self.self_norm = self_norm
        self.radar_self = radar_self
        self.other_norm = other_norm
        self.radar_other = radar_other
        self.gap = gap
        self.sigma = sigma
        self.n = n
        self.gap_score = gap_score


def build_question_lookup(questions: Iterable[Question]) -> Dict[int, Tuple[str, int]]:
    return {question.id: (question.dim, question.sign) for question in questions}


def group_other_responses(responses: Iterable[OtherResponse]) -> Dict[str, List[OtherResponse]]:
    grouped: Dict[str, List[OtherResponse]] = defaultdict(list)
    for response in responses:
        grouped[response.rater_hash].append(response)
    return grouped


def recalculate_aggregate(db: Session, session: SessionModel) -> AggregateResult:
    questions = db.query(Question).all()
    lookup = build_question_lookup(questions)

    self_rows = (
        db.query(SelfResponse)
        .filter(SelfResponse.session_id == session.id)
        
        .all()
    )
    if not self_rows:
        raise ScoringError("Self responses missing for session")

    self_answers = [(row.question_id, row.value) for row in self_rows]
    self_norm = compute_norms(self_answers, lookup)
    radar_self = norm_to_radar(self_norm)

    other_rows = (
        db.query(OtherResponse)
        .filter(OtherResponse.session_id == session.id)
        .all()
    )
    grouped = group_other_responses(other_rows)

    other_norms: List[Dict[str, float]] = []
    weights: List[float] = []
    for rater_hash, rows in grouped.items():
        answers = [(row.question_id, row.value) for row in rows]
        relation_tag = rows[0].relation_tag if rows else None
        try:
            norms = compute_norms(answers, lookup)
        except ScoringError:
            continue
        other_norms.append(norms)
        weights.append(weight_for_relation(relation_tag))

    agg_other = None
    radar_other = None
    gap = None
    sigma = None
    gap_score = None

    if other_norms:
        agg_other, sigma, gap, gap_score = compute_gap_metrics(
            self_norm, other_norms, weights
        )
        radar_other = norm_to_radar(agg_other)

    aggregate = db.get(Aggregate, session.id)
    if aggregate is None:
        aggregate = Aggregate(session_id=session.id)
        db.add(aggregate)

    aggregate.ei_self = self_norm["EI"]
    aggregate.sn_self = self_norm["SN"]
    aggregate.tf_self = self_norm["TF"]
    aggregate.jp_self = self_norm["JP"]

    if agg_other is not None and gap is not None and sigma is not None:
        aggregate.ei_other = agg_other["EI"]
        aggregate.sn_other = agg_other["SN"]
        aggregate.tf_other = agg_other["TF"]
        aggregate.jp_other = agg_other["JP"]
        aggregate.ei_gap = gap["EI"]
        aggregate.sn_gap = gap["SN"]
        aggregate.tf_gap = gap["TF"]
        aggregate.jp_gap = gap["JP"]
        aggregate.ei_sigma = sigma["EI"]
        aggregate.sn_sigma = sigma["SN"]
        aggregate.tf_sigma = sigma["TF"]
        aggregate.jp_sigma = sigma["JP"]
        aggregate.n = len(other_norms)
        aggregate.gap_score = gap_score
    else:
        aggregate.ei_other = aggregate.sn_other = aggregate.tf_other = aggregate.jp_other = None
        aggregate.ei_gap = aggregate.sn_gap = aggregate.tf_gap = aggregate.jp_gap = None
        aggregate.ei_sigma = aggregate.sn_sigma = aggregate.tf_sigma = aggregate.jp_sigma = None
        aggregate.n = 0
        aggregate.gap_score = None

    db.flush()

    return AggregateResult(
        session_id=session.id,
        mode=session.mode,
        self_norm=self_norm,
        radar_self=radar_self,
        other_norm=agg_other,
        radar_other=radar_other,
        gap=gap,
        sigma=sigma,
        n=len(other_norms),
        gap_score=gap_score,
    )
