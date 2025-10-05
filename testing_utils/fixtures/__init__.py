from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.data.questions import questions_for_mode

FIXTURES_DIR = Path(__file__).resolve().parent


def build_fake_answers(mode: str = "basic", value: int = 3) -> List[dict[str, int]]:
    """Return a deterministic answer payload covering all questions for the mode."""
    answers: List[dict[str, int]] = []
    for question in questions_for_mode(mode):
        answers.append({"question_id": question["id"], "value": value})
    return answers


def _load_json_fixture(name: str) -> dict:
    path = FIXTURES_DIR / name
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


FAKE_PARTICIPANT_PREVIEW = _load_json_fixture("participant_preview.json")
