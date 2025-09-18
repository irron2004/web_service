
from collections import Counter

from app.data.questionnaire_loader import get_question_seeds
from app.data.questions import questions_for_mode


def test_question_seed_counts():
    seeds = list(get_question_seeds())
    assert len(seeds) == 40

    contexts = Counter(seed.context for seed in seeds)
    assert contexts["common"] == 24
    assert contexts["couple"] == 8
    assert contexts["friend"] == 8

    ids = [seed.id for seed in seeds]
    assert len(ids) == len(set(ids)), "question IDs must be unique"

    codes = [seed.code for seed in seeds]
    assert len(codes) == len(set(codes)), "question codes must be unique"



def test_questions_for_mode_counts():
    basic = questions_for_mode("basic")
    assert len(basic) == 24
    assert {item["context"] for item in basic} == {"common"}

    couple = questions_for_mode("couple")
    assert len(couple) == 32
    assert {item["context"] for item in couple} == {"common", "couple"}

    friend = questions_for_mode("friend")
    assert len(friend) == 32
    assert {item["context"] for item in friend} == {"common", "friend"}
