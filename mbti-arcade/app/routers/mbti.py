from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import random
from app.database import save_evaluation, get_friend_info, get_evaluation_statistics, save_friend_info, update_actual_mbti

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# MBTI 질문 데이터 (24문항)
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

# MBTI 결과 데이터
MBTI_RESULTS = {
    "INTJ": {"title": "건축가", "description": "전략적 사고와 독창성을 가진 혁신가"},
    "INTP": {"title": "논리술사", "description": "논리적 분석과 창의적 문제해결을 선호하는 사상가"},
    "ENTJ": {"title": "통솔자", "description": "대담하고 상상력이 풍부한 강력한 리더"},
    "ENTP": {"title": "변론가", "description": "지적이고 호기심이 많은 사상가"},
    "INFJ": {"title": "옹호자", "description": "조용하고 신비로운 이상주의자"},
    "INFP": {"title": "중재자", "description": "시적이고 친절한 이상주의자"},
    "ENFJ": {"title": "선도자", "description": "카리스마 있고 영감을 주는 리더"},
    "ENFP": {"title": "활동가", "description": "열정적이고 창의적인 자유로운 영혼"},
    "ISTJ": {"title": "현실주의자", "description": "실용적이고 사실에 기반한 결정을 내리는 사람"},
    "ISFJ": {"title": "수호자", "description": "매우 헌신적이고 따뜻한 수호자"},
    "ESTJ": {"title": "경영자", "description": "실용적이고 사실에 기반한 결정을 내리는 관리자"},
    "ESFJ": {"title": "집정관", "description": "매우 사교적이고 헌신적인 협력자"},
    "ISTP": {"title": "만능재주꾼", "description": "대담하고 실험적인 실용주의자"},
    "ISFP": {"title": "모험가", "description": "유연하고 매력적인 예술가"},
    "ESTP": {"title": "사업가", "description": "스마트하고 에너지 넘치는 기업가"},
    "ESFP": {"title": "연예인", "description": "자유분방하고 재미있는 연예인"},
}

@router.get("/", response_class=HTMLResponse)
async def mbti_home(request: Request):
    """MBTI 테스트 홈페이지"""
    return templates.TemplateResponse("mbti/index.html", {"request": request})

@router.get("/self-test", response_class=HTMLResponse)
async def self_test(request: Request):
    """내 MBTI 테스트 페이지"""
    questions = MBTI_QUESTIONS.copy()
    random.shuffle(questions)
    
    return templates.TemplateResponse("mbti/self_test.html", {
        "request": request, 
        "questions": questions
    })

@router.get("/friend-system", response_class=HTMLResponse)
async def friend_system_info(request: Request):
    """친구 평가 시스템 설명 페이지"""
    return templates.TemplateResponse("mbti/friend_system.html", {
        "request": request
    })

@router.get("/friend", response_class=HTMLResponse)
async def friend_input(request: Request):
    """친구 정보 입력 페이지"""
    return templates.TemplateResponse("mbti/friend_input.html", {"request": request})

@router.post("/friend", response_class=HTMLResponse)
async def friend_input_post(request: Request, 
                          friend_name: str = Form(...),
                          friend_email: str = Form(...),
                          my_perspective: str = Form(...),
                          friend_description: str = Form("")):
    """친구 정보 저장 및 테스트 페이지로 리다이렉트"""
    save_friend_info(friend_email, friend_name, friend_description, my_perspective)
    return RedirectResponse(url=f"/mbti/test?friend_email={friend_email}", status_code=303)

@router.post("/update_actual_mbti", response_class=HTMLResponse)
async def update_actual_mbti_post(request: Request,
                                friend_email: str = Form(...),
                                actual_mbti: str = Form(...)):
    """실제 MBTI 업데이트"""
    success = update_actual_mbti(friend_email, actual_mbti)
    if success:
        return RedirectResponse(url=f"/mbti/friend/{friend_email}", status_code=303)
    else:
        return RedirectResponse(url="/mbti/friend", status_code=303)

@router.get("/friend/{friend_email}", response_class=HTMLResponse)
async def friend_results(request: Request, friend_email: str):
    """친구 평가 결과 페이지"""
    friend_info = get_friend_info(friend_email)
    if not friend_info:
        return RedirectResponse(url="/mbti/friend", status_code=303)
    
    statistics = get_evaluation_statistics(friend_email)
    
    return templates.TemplateResponse("mbti/friend_results.html", {
        "request": request,
        "friend_info": friend_info,
        "statistics": statistics
    })

@router.get("/test", response_class=HTMLResponse)
async def mbti_test(request: Request):
    """MBTI 테스트 페이지"""
    questions = MBTI_QUESTIONS.copy()
    random.shuffle(questions)
    
    # 친구 정보 가져오기
    friend_email = request.query_params.get('friend_email', '')
    friend_info = None
    if friend_email:
        friend_info = get_friend_info(friend_email)
    
    return templates.TemplateResponse("mbti/test.html", {
        "request": request, 
        "questions": questions,
        "friend_info": friend_info
    })

@router.post("/result", response_class=HTMLResponse)
async def mbti_result(request: Request):
    """MBTI 결과 페이지"""
    form_data = await request.form()
    
    # 친구 정보 추출
    friend_email = form_data.get("friend_email", "")
    evaluator_name = form_data.get("evaluator_name", "")
    my_perspective = form_data.get("my_perspective", "")
    
    # Likert 5점 척도 점수 계산
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    raw_scores = {"E-I": 0, "S-N": 0, "T-F": 0, "J-P": 0}
    responses = {}
    
    for key, value in form_data.items():
        if key.startswith("q"):
            question_id = int(key[1:])
            responses[question_id] = int(value)
            question = next((q for q in MBTI_QUESTIONS if q["id"] == question_id), None)
            if question:
                # 응답값을 1-5에서 -2~+2로 변환 (중앙값 3 기준 편차)
                response_value = int(value)
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
    
    result = MBTI_RESULTS.get(mbti_type, {"title": "알 수 없음", "description": "결과를 분석할 수 없습니다."})
    
    # 친구 평가인 경우 데이터베이스에 저장
    if friend_email:
        evaluation_data = {
            'friend_email': friend_email,
            'evaluator_name': evaluator_name,
            'responses': responses,
            'mbti_type': mbti_type,
            'scores': scores,
            'raw_scores': raw_scores
        }
        save_evaluation(friend_email, evaluation_data)
    
    return templates.TemplateResponse("mbti/result.html", {
        "request": request,
        "mbti_type": mbti_type,
        "result": result,
        "scores": scores,
        "raw_scores": raw_scores,
        "friend_email": friend_email,
        "evaluator_name": evaluator_name
    })

@router.post("/self-result", response_class=HTMLResponse)
async def self_mbti_result(request: Request):
    """내 MBTI 테스트 결과 페이지"""
    form_data = await request.form()
    
    # Likert 5점 척도 점수 계산
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    raw_scores = {"E-I": 0, "S-N": 0, "T-F": 0, "J-P": 0}
    responses = {}
    
    for key, value in form_data.items():
        if key.startswith("q"):
            question_id = int(key[1:])
            responses[question_id] = int(value)
            question = next((q for q in MBTI_QUESTIONS if q["id"] == question_id), None)
            if question:
                # 응답값을 1-5에서 -2~+2로 변환 (중앙값 3 기준 편차)
                response_value = int(value)
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
    
    result = MBTI_RESULTS.get(mbti_type, {"title": "알 수 없음", "description": "결과를 분석할 수 없습니다."})
    
    return templates.TemplateResponse("mbti/self_result.html", {
        "request": request,
        "mbti_type": mbti_type,
        "result": result,
        "scores": scores,
        "raw_scores": raw_scores
    })

@router.get("/types", response_class=HTMLResponse)
async def mbti_types(request: Request):
    """MBTI 유형 설명 페이지"""
    return templates.TemplateResponse("mbti/types.html", {
        "request": request,
        "mbti_results": MBTI_RESULTS
    }) 

@router.get("/share", response_class=HTMLResponse)
async def mbti_share_form(request: Request, name: str = Query(None), email: str = Query(None), mbti: str = Query(None)):
    """MBTI 결과 공유 폼 (이름, 이메일, MBTI 입력, 검사 버튼)"""
    return templates.TemplateResponse("mbti/share.html", {
        "request": request,
        "name": name or "",
        "email": email or "",
        "mbti": mbti or ""
    })

@router.post("/share", response_class=HTMLResponse)
async def mbti_share_post(request: Request):
    form = await request.form()
    name = form.get("name", "")
    email = form.get("email", "")
    mbti = form.get("mbti", "")
    # 공유 링크 생성 (쿼리 파라미터로 전달)
    share_url = f"/mbti/share?name={name}&email={email}&mbti={mbti}"
    return templates.TemplateResponse("mbti/share_success.html", {
        "request": request,
        "share_url": share_url,
        "name": name,
        "email": email,
        "mbti": mbti
    }) 