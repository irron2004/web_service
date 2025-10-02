from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True, slots=True)
class Problem:
    question: str
    answer: int
    hint: str | None = None


_PROBLEM_DATA: Dict[str, List[Problem]] = {
    "덧셈": [
        Problem(question="15 + 23 = ?", answer=38),
        Problem(question="47 + 18 = ?", answer=65),
        Problem(question="32 + 45 = ?", answer=77),
        Problem(question="56 + 29 = ?", answer=85),
        Problem(question="78 + 34 = ?", answer=112),
    ],
    "뺄셈": [
        Problem(question="45 - 12 = ?", answer=33),
        Problem(question="67 - 23 = ?", answer=44),
        Problem(question="89 - 34 = ?", answer=55),
        Problem(question="123 - 45 = ?", answer=78),
        Problem(question="156 - 67 = ?", answer=89),
    ],
    "곱셈": [
        Problem(question="7 × 8 = ?", answer=56),
        Problem(question="6 × 9 = ?", answer=54),
        Problem(question="4 × 12 = ?", answer=48),
        Problem(question="9 × 7 = ?", answer=63),
        Problem(question="8 × 6 = ?", answer=48),
    ],
    "나눗셈": [
        Problem(question="56 ÷ 7 = ?", answer=8),
        Problem(question="72 ÷ 8 = ?", answer=9),
        Problem(question="45 ÷ 5 = ?", answer=9),
        Problem(question="63 ÷ 9 = ?", answer=7),
        Problem(question="48 ÷ 6 = ?", answer=8),
    ],
}


def list_categories() -> List[str]:
    return list(_PROBLEM_DATA.keys())


def get_random_problem(category: str) -> Problem:
    import random

    problems = get_problems(category)
    return random.choice(problems)


def get_problems(category: str) -> List[Problem]:
    return _PROBLEM_DATA.get(category, _PROBLEM_DATA[list_categories()[0]])


__all__ = ["Problem", "list_categories", "get_problems", "get_random_problem"]
