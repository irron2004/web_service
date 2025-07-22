from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from app.core.db import get_session
from app.core.services.mbti_service import MBTIService
from app.core.token import issue_token
from urllib.parse import urlencode

router = APIRouter(tags=["Share"])

@router.post("/share", response_class=HTMLResponse)
async def make_share_link(request: Request,
                          name: str = Form(...),
                          email: str = Form(None),
                          my_mbti: str = Form(...),
                          session = Depends(get_session)):
    svc = MBTIService(session)
    pair_id = await svc.create_pair("friend", None,
                                    my_name=name, my_email=email, my_mbti=my_mbti)
    token = issue_token(pair_id, my_mbti)
    share_url = str(request.base_url.replace(path=f"/quiz/{token}"))
    return RedirectResponse(url=f"/mbti/share_success?{urlencode({'url': share_url})}", status_code=303) 