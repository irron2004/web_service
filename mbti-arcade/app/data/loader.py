
from __future__ import annotations

from sqlalchemy.orm import Session

from app.data.questionnaire_loader import get_question_seeds
from app.models import Question


def seed_questions(db: Session) -> None:
    seeds = get_question_seeds()
    existing_by_code = {row.code: row for row in db.query(Question).all()}

    for seed in seeds:
        record = existing_by_code.get(seed.code)
        if record is None:
            question = Question(
                id=seed.id,
                code=seed.code,
                dim=seed.dim,
                sign=seed.sign,
                context=seed.context,
                prompt_self=seed.prompt_self,
                prompt_other=seed.prompt_other,
                theme=seed.theme,
                scenario=seed.scenario,
            )
            db.add(question)
            continue

        # Ensure fields stay in sync with the source JSON.
        record.dim = seed.dim
        record.sign = seed.sign
        record.context = seed.context
        record.prompt_self = seed.prompt_self
        record.prompt_other = seed.prompt_other
        record.theme = seed.theme
        record.scenario = seed.scenario
        if record.id != seed.id:
            record.id = seed.id

    db.commit()
