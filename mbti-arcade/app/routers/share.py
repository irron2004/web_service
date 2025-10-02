from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.db import get_session
from app.core.services.mbti_service import MBTIService
from app.core.token import issue_token

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Share"])
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

@router.post("/share", response_class=HTMLResponse)
@limiter.limit("1/minute")
def make_share_link(request: Request,
                   name: str = Form(...),
                   email: str = Form(None),
                   my_mbti: str = Form(...),
                   session = Depends(get_session)):
    svc = MBTIService(session)
    pair_id = svc.create_pair("friend", None,
                              my_name=name, my_email=email, my_mbti=my_mbti)
    token = issue_token(pair_id, my_mbti)
    share_url = str(request.base_url.replace(path=f"/quiz/{token}"))
    return RedirectResponse(url=f"/mbti/share_success?{urlencode({'url': share_url})}", status_code=303) 