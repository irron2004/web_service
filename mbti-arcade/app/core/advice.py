ADVICE_MATRIX = {
  ("E","I"): "당신은 외향적, 친구는 내향적입니다. 대화 시 배려를!",
  ("I","E"): "당신은 내향적, 친구는 외향적입니다. 때로는 적극적으로 표현해보세요.",
  # ... 32개 문장 추가 가능 ...
}

def build_advice(my_mbti: str, friend_mbti: str) -> str:
    advice = []
    for i, dims in enumerate(zip(my_mbti, friend_mbti)):
        if dims[0] == dims[1]: continue
        advice.append(ADVICE_MATRIX.get((dims[0], dims[1]), "서로의 차이를 존중하세요."))
    return " ".join(advice) 