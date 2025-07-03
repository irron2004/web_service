#!/usr/bin/env python3
"""
MBTI 점수 계산 로직 테스트 스크립트
"""

# MBTI 질문 데이터 (app/routers/mbti.py에서 복사)
MBTI_QUESTIONS = [
    # E/I 지표 (1-6번)
    {"id": 1, "question": "그 사람은 처음 만난 사람과도 쉽게 대화를 시작한다.", "type": "E-I", "sign": 1},
    {"id": 2, "question": "그 사람은 큰 모임보다 소수의 친한 사람들과 시간을 보내는 것을 더 선호한다.", "type": "E-I", "sign": -1},
    {"id": 3, "question": "그 사람은 친구 모임에서 이야기의 중심이 되는 경우가 많다.", "type": "E-I", "sign": 1},
    {"id": 4, "question": "그 사람은 하루를 마친 뒤 혼자만의 시간을 가져야 에너지가 충전된다.", "type": "E-I", "sign": -1},
    {"id": 5, "question": "그 사람은 대화를 종종 즉흥적으로 주도한다.", "type": "E-I", "sign": 1},
    {"id": 6, "question": "그 사람은 파티보다 조용한 독서 시간을 더 기대한다.", "type": "E-I", "sign": -1},
    
    # S/N 지표 (7-12번)
    {"id": 7, "question": "그 사람은 세부 정보와 사실을 중시해 결정을 내린다.", "type": "S-N", "sign": 1},
    {"id": 8, "question": "그 사람은 아이디어와 가능성을 자유롭게 상상한다.", "type": "S-N", "sign": -1},
    {"id": 9, "question": "그 사람은 이미 검증된 방법을 우선시한다.", "type": "S-N", "sign": 1},
    {"id": 10, "question": "그 사람은 패턴과 추세를 빠르게 파악한다.", "type": "S-N", "sign": -1},
    {"id": 11, "question": "그 사람은 설명보다 직접 해보는 것을 선호한다.", "type": "S-N", "sign": 1},
    {"id": 12, "question": "그 사람은 미래 시나리오에 대한 토론을 즐긴다.", "type": "S-N", "sign": -1},
    
    # T/F 지표 (13-18번)
    {"id": 13, "question": "그 사람은 결정을 내릴 때 논리적 근거를 먼저 확인한다.", "type": "T-F", "sign": 1},
    {"id": 14, "question": "그 사람은 다른 사람의 감정을 깊이 고려한다.", "type": "T-F", "sign": -1},
    {"id": 15, "question": "그 사람은 대화할 때 사실과 수치를 인용한다.", "type": "T-F", "sign": 1},
    {"id": 16, "question": "그 사람은 갈등을 피하고 조화를 만들려 노력한다.", "type": "T-F", "sign": -1},
    {"id": 17, "question": "그 사람은 냉철한 피드백을 주는 편이다.", "type": "T-F", "sign": 1},
    {"id": 18, "question": "그 사람은 상대방이 상처받지 않도록 말투를 조심한다.", "type": "T-F", "sign": -1},
    
    # J/P 지표 (19-24번)
    {"id": 19, "question": "그 사람은 계획을 세우고 일정표를 지키려 노력한다.", "type": "J-P", "sign": 1},
    {"id": 20, "question": "그 사람은 변수가 생기면 즉시 방향을 바꿀 수 있다.", "type": "J-P", "sign": -1},
    {"id": 21, "question": "그 사람은 일을 시작하기 전에 목록을 작성한다.", "type": "J-P", "sign": 1},
    {"id": 22, "question": "그 사람은 기한이 다가와야 집중력이 높아진다.", "type": "J-P", "sign": -1},
    {"id": 23, "question": "그 사람은 결정된 뒤에도 더 나은 옵션을 계속 탐색한다.", "type": "J-P", "sign": -1},
    {"id": 24, "question": "그 사람은 미리 해야 할 일을 끝내야 마음이 편하다.", "type": "J-P", "sign": 1},
]

def calculate_mbti_score(responses):
    """MBTI 점수 계산 함수"""
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    raw_scores = {"E-I": 0, "S-N": 0, "T-F": 0, "J-P": 0}
    
    for question in MBTI_QUESTIONS:
        question_id = question["id"]
        if str(question_id) in responses:
            # 응답값을 1-5에서 -2~+2로 변환 (중앙값 3 기준 편차)
            response_value = int(responses[str(question_id)])
            deviation = response_value - 3
            
            # 가중치 부호 적용
            weighted_score = question["sign"] * deviation
            
            # 지표별 누적 합산
            if question["type"] == "E-I":
                raw_scores["E-I"] += weighted_score
            elif question["type"] == "S-N":
                raw_scores["S-N"] += weighted_score
            elif question["type"] == "T-F":
                raw_scores["T-F"] += weighted_score
            elif question["type"] == "J-P":
                raw_scores["J-P"] += weighted_score
    
    # 각 지표별 최대 가능 점수 (6문항 × 2 = 12)
    max_score = 12
    
    # 백분율 계산 및 개별 점수 설정
    if raw_scores["E-I"] > 0:
        e_percent = min(100, ((raw_scores["E-I"] + max_score) / (2 * max_score)) * 100)
        scores["E"] = int(e_percent)
        scores["I"] = 100 - scores["E"]
    else:
        i_percent = min(100, ((-raw_scores["E-I"] + max_score) / (2 * max_score)) * 100)
        scores["I"] = int(i_percent)
        scores["E"] = 100 - scores["I"]
    
    if raw_scores["S-N"] > 0:
        s_percent = min(100, ((raw_scores["S-N"] + max_score) / (2 * max_score)) * 100)
        scores["S"] = int(s_percent)
        scores["N"] = 100 - scores["S"]
    else:
        n_percent = min(100, ((-raw_scores["S-N"] + max_score) / (2 * max_score)) * 100)
        scores["N"] = int(n_percent)
        scores["S"] = 100 - scores["N"]
    
    if raw_scores["T-F"] > 0:
        t_percent = min(100, ((raw_scores["T-F"] + max_score) / (2 * max_score)) * 100)
        scores["T"] = int(t_percent)
        scores["F"] = 100 - scores["T"]
    else:
        f_percent = min(100, ((-raw_scores["T-F"] + max_score) / (2 * max_score)) * 100)
        scores["F"] = int(f_percent)
        scores["T"] = 100 - scores["F"]
    
    if raw_scores["J-P"] > 0:
        j_percent = min(100, ((raw_scores["J-P"] + max_score) / (2 * max_score)) * 100)
        scores["J"] = int(j_percent)
        scores["P"] = 100 - scores["J"]
    else:
        p_percent = min(100, ((-raw_scores["J-P"] + max_score) / (2 * max_score)) * 100)
        scores["P"] = int(p_percent)
        scores["J"] = 100 - scores["P"]
    
    # MBTI 유형 결정
    mbti_type = ""
    mbti_type += "E" if raw_scores["E-I"] > 0 else "I"
    mbti_type += "S" if raw_scores["S-N"] > 0 else "N"
    mbti_type += "T" if raw_scores["T-F"] > 0 else "F"
    mbti_type += "J" if raw_scores["J-P"] > 0 else "P"
    
    return {
        "mbti_type": mbti_type,
        "scores": scores,
        "raw_scores": raw_scores
    }

def test_extreme_e():
    """극단적인 E 성향 테스트"""
    print("🧪 테스트 1: 극단적인 외향성 (E) 성향")
    responses = {}
    
    # 모든 E 관련 질문에 5점, I 관련 질문에 1점
    for question in MBTI_QUESTIONS:
        if question["type"] == "E-I":
            if question["sign"] == 1:  # E 질문
                responses[str(question["id"])] = "5"
            else:  # I 질문
                responses[str(question["id"])] = "1"
        else:
            # 다른 지표는 중립 (3점)
            responses[str(question["id"])] = "3"
    
    result = calculate_mbti_score(responses)
    print(f"예상 결과: E가 매우 높아야 함")
    print(f"실제 결과: {result['mbti_type']}")
    print(f"E 점수: {result['scores']['E']}%, I 점수: {result['scores']['I']}%")
    print(f"Raw E-I: {result['raw_scores']['E-I']}")
    print()

def test_extreme_i():
    """극단적인 I 성향 테스트"""
    print("🧪 테스트 2: 극단적인 내향성 (I) 성향")
    responses = {}
    
    # 모든 I 관련 질문에 5점, E 관련 질문에 1점
    for question in MBTI_QUESTIONS:
        if question["type"] == "E-I":
            if question["sign"] == -1:  # I 질문
                responses[str(question["id"])] = "5"
            else:  # E 질문
                responses[str(question["id"])] = "1"
        else:
            # 다른 지표는 중립 (3점)
            responses[str(question["id"])] = "3"
    
    result = calculate_mbti_score(responses)
    print(f"예상 결과: I가 매우 높아야 함")
    print(f"실제 결과: {result['mbti_type']}")
    print(f"E 점수: {result['scores']['E']}%, I 점수: {result['scores']['I']}%")
    print(f"Raw E-I: {result['raw_scores']['E-I']}")
    print()

def test_intj():
    """INTJ 성향 테스트"""
    print("🧪 테스트 3: INTJ 성향 테스트")
    responses = {}
    
    for question in MBTI_QUESTIONS:
        if question["type"] == "E-I":
            # I 성향 (내향성)
            if question["sign"] == -1:  # I 질문
                responses[str(question["id"])] = "5"
            else:  # E 질문
                responses[str(question["id"])] = "1"
        elif question["type"] == "S-N":
            # N 성향 (직관)
            if question["sign"] == -1:  # N 질문
                responses[str(question["id"])] = "5"
            else:  # S 질문
                responses[str(question["id"])] = "1"
        elif question["type"] == "T-F":
            # T 성향 (사고)
            if question["sign"] == 1:  # T 질문
                responses[str(question["id"])] = "5"
            else:  # F 질문
                responses[str(question["id"])] = "1"
        elif question["type"] == "J-P":
            # J 성향 (판단)
            if question["sign"] == 1:  # J 질문
                responses[str(question["id"])] = "5"
            else:  # P 질문
                responses[str(question["id"])] = "1"
    
    result = calculate_mbti_score(responses)
    print(f"예상 결과: INTJ")
    print(f"실제 결과: {result['mbti_type']}")
    print(f"점수: E:{result['scores']['E']}% I:{result['scores']['I']}% S:{result['scores']['S']}% N:{result['scores']['N']}% T:{result['scores']['T']}% F:{result['scores']['F']}% J:{result['scores']['J']}% P:{result['scores']['P']}%")
    print()

def test_neutral():
    """중립 성향 테스트"""
    print("🧪 테스트 4: 중립 성향 테스트 (모든 질문 3점)")
    responses = {}
    
    # 모든 질문에 3점 (중립)
    for question in MBTI_QUESTIONS:
        responses[str(question["id"])] = "3"
    
    result = calculate_mbti_score(responses)
    print(f"예상 결과: 모든 지표가 50% 근처")
    print(f"실제 결과: {result['mbti_type']}")
    print(f"점수: E:{result['scores']['E']}% I:{result['scores']['I']}% S:{result['scores']['S']}% N:{result['scores']['N']}% T:{result['scores']['T']}% F:{result['scores']['F']}% J:{result['scores']['J']}% P:{result['scores']['P']}%")
    print()

if __name__ == "__main__":
    print("🎯 MBTI 점수 계산 로직 테스트")
    print("=" * 50)
    
    test_extreme_e()
    test_extreme_i()
    test_intj()
    test_neutral()
    
    print("✅ 테스트 완료!")
    print("\n💡 브라우저에서 http://localhost:8000 으로 접속하여 실제 테스트를 해보세요!") 