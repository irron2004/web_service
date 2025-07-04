"""
간단한 인메모리 데이터베이스
실제 배포 시에는 SQLite, PostgreSQL 등을 사용하세요.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

# 데이터 저장소
friend_evaluations: Dict[str, List] = {}  # email -> evaluations
friend_info: Dict[str, dict] = {}  # email -> friend_info

def save_evaluation(friend_email: str, evaluation_data: dict):
    """평가 결과 저장"""
    if friend_email not in friend_evaluations:
        friend_evaluations[friend_email] = []
    
    evaluation_data['created_at'] = datetime.now().isoformat()
    friend_evaluations[friend_email].append(evaluation_data)
    
    # 간단한 파일 저장 (선택사항)
    save_to_file()

def get_friend_evaluations(friend_email: str) -> List[dict]:
    """친구의 모든 평가 결과 조회"""
    return friend_evaluations.get(friend_email, [])

def save_friend_info(email: str, name: str, description: str = "", my_perspective: str = ""):
    """친구 정보 저장"""
    friend_info[email] = {
        'name': name,
        'email': email,
        'description': description,
        'my_perspective': my_perspective,
        'created_at': datetime.now().isoformat()
    }
    save_to_file()

def update_actual_mbti(email: str, actual_mbti: str):
    """실제 MBTI 업데이트"""
    if email in friend_info:
        friend_info[email]['actual_mbti'] = actual_mbti
        friend_info[email]['mbti_updated_at'] = datetime.now().isoformat()
        save_to_file()
        return True
    return False

def get_friend_info(email: str) -> Optional[dict]:
    """친구 정보 조회"""
    return friend_info.get(email)

def get_evaluation_statistics(friend_email: str) -> dict:
    """평가 통계 계산"""
    evaluations = get_friend_evaluations(friend_email)
    
    if not evaluations:
        return {
            'total_evaluations': 0,
            'mbti_distribution': {},
            'average_scores': {},
            'recent_evaluations': []
        }
    
    # MBTI 분포 계산
    mbti_distribution = {}
    total_scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    
    for eval in evaluations:
        mbti_type = eval.get('mbti_type', 'UNKNOWN')
        mbti_distribution[mbti_type] = mbti_distribution.get(mbti_type, 0) + 1
        
        scores = eval.get('scores', {})
        for key in total_scores:
            total_scores[key] += scores.get(key, 0)
    
    # 평균 점수 계산
    count = len(evaluations)
    average_scores = {key: round(value / count, 1) for key, value in total_scores.items()}
    
    # 최근 평가 (최대 5개)
    recent_evaluations = sorted(evaluations, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    return {
        'total_evaluations': count,
        'mbti_distribution': mbti_distribution,
        'average_scores': average_scores,
        'recent_evaluations': recent_evaluations
    }

def save_to_file():
    """데이터를 파일에 저장 (선택사항)"""
    try:
        data = {
            'friend_evaluations': friend_evaluations,
            'friend_info': friend_info
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"데이터 저장 실패: {e}")

def load_from_file():
    """파일에서 데이터 로드 (선택사항)"""
    global friend_evaluations, friend_info
    try:
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                friend_evaluations = data.get('friend_evaluations', {})
                friend_info = data.get('friend_info', {})
    except Exception as e:
        print(f"데이터 로드 실패: {e}")

# 서버 시작 시 데이터 로드
load_from_file() 