from itsdangerous import URLSafeTimedSerializer
import os

_signer = URLSafeTimedSerializer(os.getenv("SECRET_KEY", "dev-key"))

def issue_token(pair_id: str, my_mbti: str) -> str:
    payload = f"{pair_id}.{my_mbti}"
    return _signer.dumps(payload)

def verify_token(token: str, max_age=3600) -> tuple[str, str]:
    """return (pair_id, my_mbti)"""
    data = _signer.loads(token, max_age=max_age)
    pid, my_mbti = data.split(".", 1)
    return pid, my_mbti 