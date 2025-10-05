from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from sqlalchemy.orm import Session

from app.data.loader import seed_questions
from app.database import SessionLocal
from app.models import (
    OtherResponse,
    Participant,
    ParticipantAnswer,
    ParticipantRelation,
    Question,
    Session as SessionModel,
)
from app.services.aggregator import (
    build_question_lookup,
    group_other_responses,
    recalculate_aggregate,
    recalculate_relation_aggregates,
)
from app.services.scoring import ScoringError, compute_norms, norms_to_mbti

LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "backfill_participants.log"
RELATION_DEFAULT = ParticipantRelation.OTHER


def _ensure_log_path() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _normalize_relation(tag: str | None) -> ParticipantRelation:
    if not tag:
        return RELATION_DEFAULT
    try:
        return ParticipantRelation(tag)
    except ValueError:
        return RELATION_DEFAULT


def _participant_rater_hash(participant_id: int) -> str:
    return f"participant:{participant_id}"

def _participant_answers(rows: Iterable[OtherResponse]) -> List[tuple[int, int]]:
    return [(row.question_id, row.value) for row in rows]


def _load_questions(db: Session) -> Dict[int, tuple[str, int]]:
    questions = db.query(Question).all()
    return build_question_lookup(questions)


def backfill_participants(dry_run: bool = False) -> Dict[str, int]:
    summary = {
        "sessions_processed": 0,
        "participants_created": 0,
        "answers_copied": 0,
        "aggregates_recalculated": 0,
        "dry_run": dry_run,
    }

    db = SessionLocal()
    try:
        seed_questions(db)
        lookup = _load_questions(db)

        sessions = db.query(SessionModel).all()
        for session in sessions:
            other_rows = (
                db.query(OtherResponse)
                .filter(OtherResponse.session_id == session.id)
                .all()
            )
            if not other_rows:
                continue

            grouped = group_other_responses(other_rows)
            if not grouped:
                continue

            summary["sessions_processed"] += 1

            for rater_hash, rows in grouped.items():
                participant = None
                if rows and rows[0].participant_id is not None:
                    participant = db.get(Participant, rows[0].participant_id)

                if participant is None:
                    participant = Participant(
                        session_id=session.id,
                        invite_token=session.invite_token,
                        relation=_normalize_relation(rows[0].relation_tag),
                    )
                    db.add(participant)
                    db.flush()
                    summary["participants_created"] += 1

                for row in rows:
                    row.participant_id = participant.id

                db.query(ParticipantAnswer).filter(
                    ParticipantAnswer.participant_id == participant.id
                ).delete()

                for row in rows:
                    db.add(
                        ParticipantAnswer(
                            participant_id=participant.id,
                            question_id=row.question_id,
                            value=row.value,
                        )
                    )
                    summary["answers_copied"] += 1

                answers = _participant_answers(rows)
                try:
                    norms = compute_norms(answers, lookup)
                except ScoringError:
                    continue

                participant.axes_payload = {dim: round(value, 6) for dim, value in norms.items()}
                participant.perceived_type = norms_to_mbti(norms)
                latest_ts = max((row.created_at for row in rows if row.created_at), default=None)
                if latest_ts is None:
                    latest_ts = datetime.now(timezone.utc)
                participant.answers_submitted_at = latest_ts
                participant.computed_at = datetime.now(timezone.utc)

                new_rater_hash = _participant_rater_hash(participant.id)
                if rater_hash != new_rater_hash:
                    db.query(OtherResponse).filter(
                        OtherResponse.session_id == session.id,
                        OtherResponse.rater_hash == new_rater_hash,
                    ).delete()
                    for row in rows:
                        row.rater_hash = new_rater_hash

            try:
                recalculate_aggregate(db, session)
            except ScoringError:
                pass

            relation_summary = recalculate_relation_aggregates(session.id, db)
            if relation_summary.relations:
                summary["aggregates_recalculated"] += 1

        if dry_run:
            db.rollback()
        else:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return summary


def log_summary(summary: Dict[str, int]) -> None:
    _ensure_log_path()
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = {"timestamp": timestamp, "summary": summary}
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill participants from legacy responses")
    parser.add_argument("--dry-run", action="store_true", help="Execute without committing database changes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = backfill_participants(dry_run=args.dry_run)
    log_summary(summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
