
"""Utilities for loading the questionnaire seed dataset."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from pydantic import BaseModel, Field, field_validator

DIMENSIONS = {"EI", "SN", "TF", "JP"}
MODE_CONTEXT_MAP = {
    "romance": "couple",
    "friend": "friend",
    "work": "work",
    "partner": "partner",
    "family": "family",
}
PREFIX_BASE = {
    "C": 0,
    "R": 400,
    "F": 800,  # friend
    "W": 1200, # work
    "P": 1600, # partner
    "G": 2000, # family (G for "family")
}
DIMENSION_OFFSETS = {"EI": 0, "SN": 100, "TF": 200, "JP": 300}
CONTEXT_SORT_ORDER = {
    "common": 0,
    "couple": 1,
    "friend": 2,
    "work": 3,
    "partner": 4,
    "family": 5,
}
QUESTIONNAIRE_ENV_VAR = "QUESTIONNAIRE_FILE"


class QuestionContextModel(BaseModel):
    theme: str
    scenario: str

    model_config = {
        "extra": "forbid",
        "frozen": True,
    }


class QuestionRecordModel(BaseModel):
    id: str = Field(min_length=1)
    dim: str
    sign: int
    prompt_self: str
    prompt_other: str
    context: QuestionContextModel

    model_config = {
        "extra": "forbid",
        "frozen": True,
    }

    @field_validator("dim")
    @classmethod
    def _normalize_dim(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in DIMENSIONS:
            raise ValueError(f"Unsupported dimension '{value}'")
        return normalized

    @field_validator("sign")
    @classmethod
    def _validate_sign(cls, value: int) -> int:
        if value not in (-1, 1):
            raise ValueError("sign must be -1 or 1")
        return value


class QuestionCollectionsModel(BaseModel):
    common: List[QuestionRecordModel]
    modes: Dict[str, List[QuestionRecordModel]]

    model_config = {
        "extra": "forbid",
        "frozen": True,
    }


class QuestionnaireModel(BaseModel):
    metadata: Dict[str, object]
    dimensions: Dict[str, object]
    questions: QuestionCollectionsModel

    model_config = {
        "extra": "forbid",
        "frozen": True,
    }


@dataclass(frozen=True)
class QuestionSeed:
    id: int
    code: str
    dim: str
    sign: int
    context: str
    prompt_self: str
    prompt_other: str
    theme: str
    scenario: str


def _resolve_questionnaire_path() -> Path:
    env_override = os.getenv(QUESTIONNAIRE_ENV_VAR)
    if env_override:
        candidate = Path(env_override).expanduser()
        if not candidate.exists():
            raise FileNotFoundError(f"Questionnaire file not found: {candidate}")
        return candidate

    root = Path(__file__).resolve()
    for parent in root.parents:
        candidate = parent / "docs" / "questionnaire.v1.json"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Unable to locate questionnaire.v1.json relative to loader")


def _load_raw_payload(path: Path) -> Dict[str, object]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise TypeError('Questionnaire root must be a JSON object')
    return data


@lru_cache(maxsize=1)
def get_questionnaire(path: Path | None = None) -> QuestionnaireModel:
    resolved = path if path else _resolve_questionnaire_path()
    payload = _load_raw_payload(resolved)
    return QuestionnaireModel.model_validate(payload)


def _compute_numeric_id(code: str, dim: str, ordinal: int) -> int:
    prefix = code.split("-", 1)[0]
    base = PREFIX_BASE.get(prefix)
    if base is None:
        raise ValueError(f"Unsupported code prefix '{prefix}' for question '{code}'")
    dim_offset = DIMENSION_OFFSETS[dim]
    return base + dim_offset + ordinal


def _extract_ordinal(code: str) -> int:
    tail = code.split("-")[-1]
    try:
        ordinal = int(tail)
    except ValueError as exc:
        raise ValueError(f"Question code '{code}' has non-numeric suffix '{tail}'") from exc
    if ordinal <= 0:
        raise ValueError(f"Question code '{code}' ordinal must be positive")
    return ordinal


def _iter_question_records(questionnaire: QuestionnaireModel) -> Iterable[QuestionSeed]:
    seen_codes: set[str] = set()

    def emit(record: QuestionRecordModel, context: str) -> QuestionSeed:
        code = record.id
        if code in seen_codes:
            raise ValueError(f"Duplicate question code detected: {code}")
        ordinal = _extract_ordinal(code)
        numeric_id = _compute_numeric_id(code, record.dim, ordinal)
        seen_codes.add(code)
        return QuestionSeed(
            id=numeric_id,
            code=code,
            dim=record.dim,
            sign=record.sign,
            context=context,
            prompt_self=record.prompt_self,
            prompt_other=record.prompt_other,
            theme=record.context.theme,
            scenario=record.context.scenario,
        )

    for record in questionnaire.questions.common:
        yield emit(record, "common")

    for mode_key, records in questionnaire.questions.modes.items():
        context = MODE_CONTEXT_MAP.get(mode_key)
        if context is None:
            raise ValueError(f"Unsupported mode '{mode_key}' in questionnaire input")
        for record in records:
            yield emit(record, context)


@lru_cache(maxsize=1)
def get_question_seeds() -> Sequence[QuestionSeed]:
    questionnaire = get_questionnaire()
    seeds = list(_iter_question_records(questionnaire))
    seeds.sort(key=lambda item: (CONTEXT_SORT_ORDER[item.context], item.id))
    return tuple(seeds)


def get_question_lookup() -> Dict[int, QuestionSeed]:
    return {seed.id: seed for seed in get_question_seeds()}


def get_seeds_by_context(context: str) -> List[QuestionSeed]:
    normalized = context.lower()
    if normalized not in CONTEXT_SORT_ORDER:
        raise ValueError(f"Unsupported context '{context}'")
    return [seed for seed in get_question_seeds() if seed.context == normalized]
