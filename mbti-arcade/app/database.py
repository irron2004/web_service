from sqlmodel import Session, select
from app.core.models_db import Friend, Pair, Response
from app.core.db import get_session
from typing import Dict, List, Optional
import json

async def save_evaluation(friend_email: str, evaluator_name: str, responses: Dict[int, int], 
                         mbti_type: str, scores: Dict[str, int], raw_scores: Dict[str, int]) -> bool:
    """평가 결과를 데이터베이스에 저장"""
    try:
        async with get_session() as session:
            # Pair 생성
            pair = Pair(
                mode="friend",
                friend_email=friend_email,
                my_name=evaluator_name,
                completed=True
            )
            session.add(pair)
            await session.commit()
            await session.refresh(pair)
            
            # Response 생성
            response = Response(
                pair_id=pair.id,
                role="other",
                answers=json.dumps(responses),
                mbti_type=mbti_type,
                scores=json.dumps(scores),
                raw_scores=json.dumps(raw_scores)
            )
            session.add(response)
            await session.commit()
            return True
    except Exception as e:
        print(f"Error saving evaluation: {e}")
        return False

async def get_friend_info(email: str) -> Optional[Dict]:
    """친구 정보 조회"""
    try:
        async with get_session() as session:
            result = await session.exec(select(Friend).where(Friend.email == email))
            friend = result.first()
            if friend:
                return {
                    "email": friend.email,
                    "name": friend.name,
                    "description": friend.description,
                    "actual_mbti": friend.actual_mbti
                }
            return None
    except Exception as e:
        print(f"Error getting friend info: {e}")
        return None

async def save_friend_info(name: str, email: str, description: str = None) -> bool:
    """친구 정보 저장"""
    try:
        async with get_session() as session:
            friend = Friend(
                email=email,
                name=name,
                description=description
            )
            session.add(friend)
            await session.commit()
            return True
    except Exception as e:
        print(f"Error saving friend info: {e}")
        return False

async def update_actual_mbti(email: str, mbti_type: str) -> bool:
    """실제 MBTI 타입 업데이트"""
    try:
        async with get_session() as session:
            result = await session.exec(select(Friend).where(Friend.email == email))
            friend = result.first()
            if friend:
                friend.actual_mbti = mbti_type
                await session.commit()
                return True
            return False
    except Exception as e:
        print(f"Error updating actual MBTI: {e}")
        return False

async def get_evaluation_statistics(email: str) -> Optional[Dict]:
    """평가 통계 조회"""
    try:
        async with get_session() as session:
            # 해당 친구에 대한 모든 평가 조회
            result = await session.exec(
                select(Response)
                .join(Pair)
                .where(Pair.friend_email == email)
            )
            responses = result.all()
            
            if not responses:
                return None
            
            # MBTI 분포 계산
            mbti_distribution = {}
            total_scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
            
            for response in responses:
                mbti_type = response.mbti_type
                mbti_distribution[mbti_type] = mbti_distribution.get(mbti_type, 0) + 1
                
                # 평균 점수 계산
                scores = json.loads(response.scores)
                for key, value in scores.items():
                    if key in total_scores:
                        total_scores[key] += value
            
            # 평균 계산
            count = len(responses)
            average_scores = {key: value / count for key, value in total_scores.items()}
            
            return {
                "total_evaluations": count,
                "mbti_distribution": mbti_distribution,
                "average_scores": average_scores
            }
    except Exception as e:
        print(f"Error getting evaluation statistics: {e}")
        return None 