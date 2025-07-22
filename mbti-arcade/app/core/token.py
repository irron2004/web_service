from itsdangerous import URLSafeTimedSerializer
import os

_signer = URLSafeTimedSerializer(os.getenv("SECRET_KEY", "dev-key"))

def issue_token(pair_id: str) -> str:
    return _signer.dumps(pair_id)

def verify_token(token: str, max_age=60*60*24*7) -> str:
    from itsdangerous import BadSignature, SignatureExpired
    try:
        return _signer.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        raise ValueError("invalid token") 