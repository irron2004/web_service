from __future__ import annotations

from collections import Counter, defaultdict
from statistics import fmean
from typing import Dict, Iterable, List, NamedTuple, Tuple

from sqlalchemy.orm import Session

from app.models import (
    Aggregate,
    OtherResponse,
    Participant,
    ParticipantRelation,
    Question,
    RelationAggregate,
    SelfResponse,
    Session as SessionModel,
)
from app.schemas import DIMENSIONS
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


class RelationAggregateResult(NamedTuple):
    relation: ParticipantRelation
    respondent_count: int
    top_type: str | None
    top_fraction: float | None
    second_type: str | None
    second_fraction: float | None
    consensus: float | None
    pgi: float | None
    axes_payload: Dict[str, float] | None


class RelationAggregateSummary:
    def __init__(self, session_id: str, relations: List[RelationAggregateResult]) -> None:
        self.session_id = session_id
        self.relations = relations

    @property
    def total_respondents(self) -> int:
        return sum(item.respondent_count for item in self.relations)


RELATION_MIN_RESPONDENTS = 3


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


def _load_self_norm(db: Session, session: SessionModel, lookup: Dict[int, Tuple[str, int]]) -> Dict[str, float] | None:
    aggregate = db.get(Aggregate, session.id)
    if aggregate and all(
        getattr(aggregate, f"{dim.lower()}_self") is not None for dim in DIMENSIONS
    ):
        return {
            "EI": aggregate.ei_self,
            "SN": aggregate.sn_self,
            "TF": aggregate.tf_self,
            "JP": aggregate.jp_self,
        }

    rows = (
        db.query(SelfResponse)
        .filter(SelfResponse.session_id == session.id)
        .all()
    )
    if not rows:
        return None

    answers = [(row.question_id, row.value) for row in rows]
    try:
        return compute_norms(answers, lookup)
    except ScoringError:
        return None


def _average_axes(payloads: List[Dict[str, float]]) -> Dict[str, float]:
    return {
        dim: round(fmean(item.get(dim, 0.0) for item in payloads), 6)
        for dim in DIMENSIONS
    }


def recalculate_relation_aggregates(session_id: str, db: Session) -> RelationAggregateSummary:
    session = db.get(SessionModel, session_id)
    if session is None:
        return RelationAggregateSummary(session_id=session_id, relations=[])

    questions = db.query(Question).all()
    lookup = build_question_lookup(questions)
    self_norm = _load_self_norm(db, session, lookup)

    participants = (
        db.query(Participant)
        .filter(Participant.session_id == session_id)
        .all()
    )

    relations_map: Dict[ParticipantRelation, List[Participant]] = defaultdict(list)
    for participant in participants:
        relations_map[participant.relation].append(participant)

    results: List[RelationAggregateResult] = []

    for relation, members in relations_map.items():
        submitted = [item for item in members if item.answers_submitted_at is not None]
        respondent_count = len(submitted)

        axes_payload = None
        top_type = None
        top_fraction = None
        second_type = None
        second_fraction = None
        consensus = None
        pgi = None

        axes_candidates = [item.axes_payload for item in submitted if item.axes_payload]
        if respondent_count >= RELATION_MIN_RESPONDENTS and axes_candidates:
            axes_payload = _average_axes(axes_candidates)
            type_counts = Counter(
                item.perceived_type for item in submitted if item.perceived_type
            )
            if type_counts:
                most_common = type_counts.most_common(2)
                top_type, top_count = most_common[0]
                top_fraction = round(top_count / respondent_count, 6)
                if len(most_common) > 1:
                    second_type, second_count = most_common[1]
                    second_fraction = round(second_count / respondent_count, 6)
                if second_fraction is None:
                    consensus = top_fraction
                else:
                    consensus = round(top_fraction - second_fraction, 6)

            if self_norm is not None:
                gaps = [abs(axes_payload[dim] - self_norm[dim]) for dim in DIMENSIONS]
                pgi = round(fmean(gaps) * 100, 6)

        record = (
            db.query(RelationAggregate)
            .filter(
                RelationAggregate.session_id == session_id,
                RelationAggregate.relation == relation,
            )
            .first()
        )
        if record is None:
            record = RelationAggregate(session_id=session_id, relation=relation)
            db.add(record)

        record.respondent_count = respondent_count
        record.top_type = top_type
        record.top_fraction = top_fraction
        record.second_type = second_type
        record.second_fraction = second_fraction
        record.consensus = consensus
        record.pgi = pgi
        record.axes_payload = axes_payload

        results.append(
            RelationAggregateResult(
                relation=relation,
                respondent_count=respondent_count,
                top_type=top_type,
                top_fraction=top_fraction,
                second_type=second_type,
                second_fraction=second_fraction,
                consensus=consensus,
                pgi=pgi,
                axes_payload=axes_payload,
            )
        )

    db.flush()

    # Ensure deterministic ordering for callers/tests.
    results.sort(key=lambda item: item.relation.value)

    return RelationAggregateSummary(session_id=session_id, relations=results)
