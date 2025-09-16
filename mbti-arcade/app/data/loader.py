from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.questions import QUESTIONS
from app.models import Question


def seed_questions(db: Session) -> None:
    existing_ids = set(db.execute(select(Question.id)).scalars().all())
    for payload in QUESTIONS:
        if payload["id"] in existing_ids:
            continue
        question = Question(**payload)
        db.add(question)
    db.commit()
