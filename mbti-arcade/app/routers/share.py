from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.db import get_session
from app.core.services.mbti_service import MBTIService
from app.core.token import issue_token
from urllib.parse import urlencode
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Share"])
templates = Jinja2Templates(directory="app/templates")

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