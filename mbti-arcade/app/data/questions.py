QUESTIONS = [
    {"id": 1, "dim": "EI", "sign": 1, "context": "common", "text": "나는 새 아이디어를 이야기하며 에너지를 얻는다."},
    {"id": 2, "dim": "EI", "sign": -1, "context": "common", "text": "나는 혼자 정리할 시간이 필요할 때가 많다."},
    {"id": 3, "dim": "EI", "sign": 1, "context": "common", "text": "새로운 사람들과 금방 친해지는 편이다."},
    {"id": 4, "dim": "EI", "sign": -1, "context": "common", "text": "긴 모임 후에는 조용한 시간이 꼭 필요하다."},
    {"id": 5, "dim": "EI", "sign": 1, "context": "common", "text": "내 생각을 말로 풀어 놓을수록 정리된다."},
    {"id": 6, "dim": "EI", "sign": -1, "context": "common", "text": "나는 한두 사람과 깊게 대화할 때 집중된다."},
    {"id": 7, "dim": "SN", "sign": 1, "context": "common", "text": "나는 지금 주어진 사실에 집중하는 편이다."},
    {"id": 8, "dim": "SN", "sign": -1, "context": "common", "text": "나는 가능성과 연결고리를 먼저 떠올린다."},
    {"id": 9, "dim": "SN", "sign": 1, "context": "common", "text": "구체적인 예시가 있어야 이해가 빠르다."},
    {"id": 10, "dim": "SN", "sign": -1, "context": "common", "text": "상상 속 시나리오를 자주 탐색한다."},
    {"id": 11, "dim": "SN", "sign": 1, "context": "common", "text": "작은 변화라도 근거를 확인하려 한다."},
    {"id": 12, "dim": "SN", "sign": -1, "context": "common", "text": "전체 그림이 잡혀야 세부 계획을 세운다."},
    {"id": 13, "dim": "TF", "sign": 1, "context": "common", "text": "나는 결정할 때 논리와 기준을 먼저 본다."},
    {"id": 14, "dim": "TF", "sign": -1, "context": "common", "text": "사람들의 감정 반응을 최우선으로 고려한다."},
    {"id": 15, "dim": "TF", "sign": 1, "context": "common", "text": "지적을 받으면 근거부터 확인하고 싶다."},
    {"id": 16, "dim": "TF", "sign": -1, "context": "common", "text": "갈등이 생기면 관계부터 다독이고 싶다."},
    {"id": 17, "dim": "TF", "sign": 1, "context": "common", "text": "나는 객관적인 지표로 결과를 측정한다."},
    {"id": 18, "dim": "TF", "sign": -1, "context": "common", "text": "팀원들의 마음이 편한지 자주 살핀다."},
    {"id": 19, "dim": "JP", "sign": 1, "context": "common", "text": "일정을 미리 잡아두면 안심된다."},
    {"id": 20, "dim": "JP", "sign": -1, "context": "common", "text": "상황에 맞춰 유연하게 계획을 바꾼다."},
    {"id": 21, "dim": "JP", "sign": 1, "context": "common", "text": "끝낸 일에 체크 표시하는 것을 좋아한다."},
    {"id": 22, "dim": "JP", "sign": -1, "context": "common", "text": "마감 직전이 되어야 집중이 잘 된다."},
    {"id": 23, "dim": "JP", "sign": 1, "context": "common", "text": "내 공간과 자료를 정돈해 두려 한다."},
    {"id": 24, "dim": "JP", "sign": -1, "context": "common", "text": "새로운 기회가 오면 일정이라도 먼저 잡는다."},
    {"id": 101, "dim": "EI", "sign": 1, "context": "friend", "text": "친구 모임에서 분위기를 띄우는 편이다."},
    {"id": 102, "dim": "EI", "sign": -1, "context": "friend", "text": "혼자 휴식할 시간이 없으면 금방 지친다."},
    {"id": 103, "dim": "SN", "sign": 1, "context": "friend", "text": "친구의 근황을 세세히 기억한다."},
    {"id": 104, "dim": "SN", "sign": -1, "context": "friend", "text": "친구의 장기적 목표를 함께 상상한다."},
    {"id": 105, "dim": "TF", "sign": -1, "context": "friend", "text": "친구 기분 변화를 빨리 알아차린다."},
    {"id": 106, "dim": "TF", "sign": 1, "context": "friend", "text": "친구 고민을 들으면 해결책부터 찾는다."},
    {"id": 107, "dim": "JP", "sign": 1, "context": "friend", "text": "약속 시간과 장소를 먼저 정리한다."},
    {"id": 108, "dim": "JP", "sign": -1, "context": "friend", "text": "약속 계획이 자주 바뀌어도 괜찮다."},
    {"id": 109, "dim": "EI", "sign": 1, "context": "friend", "text": "새 친구를 소개하는 일에 적극적이다."},
    {"id": 110, "dim": "TF", "sign": -1, "context": "friend", "text": "갈등이 생기면 분위기를 먼저 누그러뜨린다."},
    {"id": 111, "dim": "SN", "sign": 1, "context": "friend", "text": "친구의 작은 변화도 눈여겨본다."},
    {"id": 112, "dim": "JP", "sign": -1, "context": "friend", "text": "즉흥적인 만남이 즐겁다."},
    {"id": 201, "dim": "EI", "sign": 1, "context": "couple", "text": "상대와 하루를 자세히 공유하면 힘이 난다."},
    {"id": 202, "dim": "EI", "sign": -1, "context": "couple", "text": "상대와 떨어져 쉬는 시간이 필요하다."},
    {"id": 203, "dim": "SN", "sign": 1, "context": "couple", "text": "함께한 추억의 세부까지 기억한다."},
    {"id": 204, "dim": "SN", "sign": -1, "context": "couple", "text": "앞으로의 삶을 함께 설계하는 편이다."},
    {"id": 205, "dim": "TF", "sign": -1, "context": "couple", "text": "상대 감정의 미묘한 변화를 알아차린다."},
    {"id": 206, "dim": "TF", "sign": 1, "context": "couple", "text": "대화에서 문제의 원인을 먼저 찾는다."},
    {"id": 207, "dim": "JP", "sign": 1, "context": "couple", "text": "함께하는 계획을 일정표에 정리해 둔다."},
    {"id": 208, "dim": "JP", "sign": -1, "context": "couple", "text": "계획이 바뀌어도 금방 적응한다."},
    {"id": 209, "dim": "EI", "sign": 1, "context": "couple", "text": "상대와 대화가 길수록 관계가 깊어진다."},
    {"id": 210, "dim": "TF", "sign": -1, "context": "couple", "text": "감정적인 공감을 가장 소중히 여긴다."},
    {"id": 211, "dim": "SN", "sign": 1, "context": "couple", "text": "함께한 일상의 루틴을 세세히 챙긴다."},
    {"id": 212, "dim": "JP", "sign": -1, "context": "couple", "text": "즉흥 데이트가 둘 사이를 활기차게 한다."},
]


def questions_for_mode(mode: str):
    mode = mode.lower()
    if mode == "basic":
        return [q for q in QUESTIONS if q["context"] == "common"]
    if mode == "friend":
        return [q for q in QUESTIONS if q["context"] in {"common", "friend"}]
    if mode == "couple":
        return [q for q in QUESTIONS if q["context"] in {"common", "couple"}]
    raise ValueError(f"Unsupported mode: {mode}")
