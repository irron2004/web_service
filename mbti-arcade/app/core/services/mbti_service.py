from sqlmodel import select
from datetime import datetime
from uuid import uuid4
from app.core.models_db import Pair, Response, Friend
from typing import Dict

class MBTIService:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def _calc_scores(answers: Dict[int, int], questions):
        raw = {"E-I": 0, "S-N": 0, "T-F": 0, "J-P": 0}
        for q in questions:
            val = answers.get(q["id"])
            if val:
                deviation = val - 3
                raw[q["type"]] += q["sign"] * deviation
        max_score = 12
        def pct(v):
            return int((abs(v) + max_score) / (2*max_score) * 100)
        scores = {
            "E": pct(max(raw["E-I"], 0)),
            "I": pct(min(raw["E-I"], 0)),
            "S": pct(max(raw["S-N"], 0)),
            "N": pct(min(raw["S-N"], 0)),
            "T": pct(max(raw["T-F"], 0)),
            "F": pct(min(raw["T-F"], 0)),
            "J": pct(max(raw["J-P"], 0)),
            "P": pct(min(raw["J-P"], 0)),
        }
        mbti = (
            ("E" if raw["E-I"] > 0 else "I")
            + ("S" if raw["S-N"] > 0 else "N")
            + ("T" if raw["T-F"] > 0 else "F")
            + ("J" if raw["J-P"] > 0 else "P")
        )
        return mbti, scores, raw

    async def create_pair(self, mode: str, email: str | None, 
                         my_name: str | None = None, my_email: str | None = None, my_mbti: str | None = None) -> str:
        pair = Pair(mode=mode, friend_email=email,
                    my_name=my_name, my_email=my_email, my_mbti=my_mbti)
        self.session.add(pair)
        await self.session.commit()
        return pair.id

    async def save_response(self, pair_id: str, role: str, answers, questions, 
                          relation: str = None):
        mbti, scores, raw = self._calc_scores(answers, questions)
        resp = Response(
            pair_id=pair_id, 
            role=role,
            relation=relation,
            answers=answers, 
            mbti_type=mbti,
            scores=scores, 
            raw_scores=raw
        )
        self.session.add(resp)
        await self.session.commit()
        return resp, mbti, scores, raw 

    async def get_response(self, pair_id: str):
        from sqlmodel import select
        result = await self.session.execute(select(Response).where(Response.pair_id == pair_id))
        return result.scalars().first() 

    async def get_pair_scores(self, pair_id: str):
        from sqlmodel import select
        stmt = select(Response).where(Response.pair_id == pair_id)
        res = (await self.session.execute(stmt)).scalars().all()
        if not res:
            return None
        latest = sorted(res, key=lambda r: r.created_at)[-2:]
        return [{"role": r.role, "mbti": r.mbti_type, "scores": r.scores} for r in latest] 