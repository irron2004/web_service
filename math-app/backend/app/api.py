from fastapi import APIRouter

router = APIRouter()

@router.post("/v1/sessions")
def create_session():
    # 20문제 세트 생성 및 반환
    pass

@router.patch("/v1/problems/{id}")
def update_problem(id: int):
    # 선택 기록(시도 n=1/2)
    pass

@router.get("/v1/stats/daily")
def get_daily_stats(days: int = 30):
    # 최근 30일 기록
    pass

@router.post("/v1/alerts/daily")
def send_daily_alert():
    # 목표 달성 메일 발송
    pass 