from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from email.utils import formatdate
from http import HTTPStatus
from pathlib import Path
from typing import Dict, Iterable, Tuple
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.datastructures import Headers, URL
from starlette.middleware.trustedhost import ENFORCE_DOMAIN_WILDCARD
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send
from sqlalchemy.orm import Session as OrmSession

try:
    from starlette.middleware.proxy_headers import ProxyHeadersMiddleware
except ImportError:  # pragma: no cover - fallback for older Starlette versions
    from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

    class ProxyHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
            forwarded_proto = request.headers.get("x-forwarded-proto")
            if forwarded_proto:
                scheme = forwarded_proto.split(",")[0].strip()
                if scheme:
                    request.scope["scheme"] = scheme

            forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host")
            if forwarded_host:
                host_value = forwarded_host.split(",")[0].strip()
                if host_value:
                    hostname, _, port_text = host_value.partition(":")
                    try:
                        port = int(port_text) if port_text else None
                    except ValueError:
                        port = None
                    if port is None:
                        port = 443 if request.scope.get("scheme") == "https" else 80
                    request.scope["server"] = (hostname.lower(), port)

            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
                if client_ip:
                    client = request.scope.get("client") or (None, 0)
                    request.scope["client"] = (client_ip, client[1] or 0)

            return await call_next(request)


class ProblemDetailsTrustedHostMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        allowed_hosts: Iterable[str] | None = None,
        www_redirect: bool = True,
    ) -> None:
        if allowed_hosts is None:
            allowed_hosts = ["*"]

        patterns = list(allowed_hosts)
        for pattern in patterns:
            assert "*" not in pattern[1:], ENFORCE_DOMAIN_WILDCARD
            if pattern.startswith("*") and pattern != "*":
                assert pattern.startswith("*."), ENFORCE_DOMAIN_WILDCARD

        self.app = app
        self.allowed_hosts = patterns
        self.allow_any = "*" in patterns
        self.www_redirect = www_redirect

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.allow_any or scope["type"] not in {"http", "websocket"}:  # pragma: no cover
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        host = headers.get("host", "").split(":")[0]
        is_valid_host = False
        found_www_redirect = False
        for pattern in self.allowed_hosts:
            if host == pattern or (pattern.startswith("*") and host.endswith(pattern[1:])):
                is_valid_host = True
                break
            if f"www.{host}" == pattern:
                found_www_redirect = True

        if is_valid_host:
            await self.app(scope, receive, send)
            return

        if found_www_redirect and self.www_redirect:
            url = URL(scope=scope)
            redirect_url = url.replace(netloc=f"www.{url.netloc}")
            response = RedirectResponse(url=str(redirect_url))
            await response(scope, receive, send)
            return

        request = Request(scope, receive)
        response = problem_response(
            request,
            status=HTTPStatus.BAD_REQUEST,
            title=HTTPStatus.BAD_REQUEST.phrase,
            detail="허용되지 않은 호스트에서 요청했습니다.",
            type_suffix="invalid-host",
        )
        await response(scope, receive, send)

from app import settings
from app.core.config import REQUEST_ID_HEADER
from app.core.db import get_session as get_core_session
from app.data.loader import seed_questions
from app.data.questionnaire_loader import get_question_lookup
from app.data.questions import questions_for_mode
from app.database import Base, engine, session_scope, get_db
from app.routers import health
from app.routers import couple as couple_router
from app.routers import og as og_router
from app.routers import participants as participants_router
from app.routers import profile as profile_router
from app.routers import quiz as quiz_router
from app.routers import report as report_router
from app.routers import reporting as reporting_router
from app.routers import responses as responses_router
from app.routers import results as results_router
from app.routers import sessions as sessions_router
from app.routers import share as share_router
from app.routers import invites as invites_router
from app.observability import bind_request_id, configure_observability, reset_request_id
from app.urling import build_invite_url
from app.utils.problem_details import (
    ProblemDetailsException,
    from_exception,
    from_http_exception,
    from_validation_error,
    internal_server_error,
    problem_response,
)
from app.models import Session as SessionModel, Participant, ParticipantRelation
from app.utils.privacy import apply_noindex_headers, NOINDEX_VALUE
from app.schemas import DIMENSIONS, ParticipantRegistrationRequest
from app.services.scoring import compute_norms, norm_to_radar
from app.routers.participants import register_participant

try:  # pragma: no cover - optional dependency
    from slowapi.errors import RateLimitExceeded  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    RateLimitExceeded = None  # type: ignore[assignment]

log = logging.getLogger("perception_gap")

app = FastAPI(
    title="360Me Perception Gap Service",
    description="Self vs Others perception gap scoring with RFC 9457 errors and observability hooks.",
    version="0.9.0",
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
_calculate_base_url = settings.CALCULATE_SERVICE_BASE_URL or "/"
if _calculate_base_url != "/":
    _calculate_base_url = _calculate_base_url.rstrip("/")
templates.env.globals.setdefault("calculate_service_url", _calculate_base_url)
templates.env.globals.setdefault(
    "calculate_service_problems_url",
    f"{_calculate_base_url}/problems" if _calculate_base_url != "/" else "/problems",
)

RELATION_LABELS: dict[str, str] = {
    "friend": "친구",
    "family": "가족",
    "partner": "부부/커플",
    "coworker": "직장",
    "other": "기타",
}


def _escape_js(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    replacements = {
        "\\": "\\\\",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "\'": "\\'",
        '"': '\\"',
        "</": "<" + "\\/",
        "\u2028": "\\u2028",
        "\u2029": "\\u2029",
    }
    for search, replacement in replacements.items():
        text = text.replace(search, replacement)
    return text


templates.env.filters.setdefault("escapejs", _escape_js)

# Set up OpenTelemetry instrumentation if available.
configure_observability(app)

_allowed_hosts = list(settings.ALLOWED_HOSTS)
if "testserver" not in _allowed_hosts:
    _allowed_hosts.append("testserver")

app.add_middleware(ProxyHeadersMiddleware)
app.add_middleware(ProblemDetailsTrustedHostMiddleware, allowed_hosts=_allowed_hosts)

try:  # pragma: no cover - optional dependency hook
    from opentelemetry import trace  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    trace = None  # type: ignore[assignment]


def _build_questions(mode: str, *, perspective: str) -> list[dict[str, object]]:

    prompt_key = "prompt_other" if perspective == "other" else "prompt_self"
    questions = []
    for raw in questions_for_mode(mode):
        prompt = raw.get(prompt_key)
        if not prompt:
            continue
        questions.append(
            {
                "id": raw["id"],
                "question": prompt,
                "dim": raw["dim"],
                "sign": raw["sign"],
                "context": raw.get("context"),
                "theme": raw.get("theme"),
                "scenario": raw.get("scenario"),
            }
        )
    return questions


_QUESTION_LOOKUP = get_question_lookup()
_QUESTION_DIM_SIGN: Dict[int, Tuple[str, int]] = {
    question_id: (seed.dim, seed.sign)
    for question_id, seed in _QUESTION_LOOKUP.items()
}
_DIMENSION_LETTERS: Dict[str, Tuple[str, str]] = {
    "EI": ("E", "I"),
    "SN": ("S", "N"),
    "TF": ("T", "F"),
    "JP": ("J", "P"),
}


MBTI_SUMMARIES: Dict[str, Dict[str, str]] = {
    "ISTJ": {"title": "Logistician", "description": "Calm planners who value duty and precise execution."},
    "ISFJ": {"title": "Defender", "description": "Supportive caretakers focused on stability and trust."},
    "INFJ": {"title": "Advocate", "description": "Idealistic advisors driven by values and long-term vision."},
    "INTJ": {"title": "Architect", "description": "Independent strategists who map bold plans logically."},
    "ISTP": {"title": "Virtuoso", "description": "Adaptable troubleshooters who master hands-on challenges."},
    "ISFP": {"title": "Adventurer", "description": "Curious creators chasing experiences and personal freedom."},
    "INFP": {"title": "Mediator", "description": "Empathetic dreamers guided by meaning and authenticity."},
    "INTP": {"title": "Logician", "description": "Analytical theorists eager to explain complex systems."},
    "ESTP": {"title": "Entrepreneur", "description": "Energetic realists who improvise and seize opportunities."},
    "ESFP": {"title": "Entertainer", "description": "Expressive performers who energize any room."},
    "ENFP": {"title": "Campaigner", "description": "Enthusiastic explorers who inspire with big ideas."},
    "ENTP": {"title": "Debater", "description": "Inventive arguers who challenge limits and assumptions."},
    "ESTJ": {"title": "Executive", "description": "Organized directors who drive progress with clarity."},
    "ESFJ": {"title": "Consul", "description": "Community builders who nurture harmony and tradition."},
    "ENFJ": {"title": "Protagonist", "description": "Persuasive mentors rallying teams around shared goals."},
    "ENTJ": {"title": "Commander", "description": "Decisive leaders who align people behind ambitious targets."},
}

_DEFAULT_SUMMARY = {
    "title": "Insight Coming Soon",
    "description": "We are preparing a richer profile for this result.",
}


def _score_answers(answer_pairs: Iterable[tuple[int, int]]) -> tuple[str, Dict[str, int], Dict[str, float]]:
    normalized_pairs = list(answer_pairs)
    if not normalized_pairs:
        raise ValueError("No answers submitted")

    norms = compute_norms(normalized_pairs, _QUESTION_DIM_SIGN)
    radar = norm_to_radar(norms)

    scores: Dict[str, int] = {}
    letters: list[str] = []

    for dim in DIMENSIONS:
        if dim not in _DIMENSION_LETTERS:
            continue
        axis_value = norms[dim]
        primary, secondary = _DIMENSION_LETTERS[dim]
        primary_score = max(0, min(100, round((axis_value + 1) * 50)))
        secondary_score = 100 - primary_score
        scores[primary] = primary_score
        scores[secondary] = secondary_score
        letters.append(primary if primary_score >= secondary_score else secondary)

    mbti_type = "".join(letters)
    return mbti_type, scores, radar

app.include_router(health.router)
app.include_router(sessions_router.router)
app.include_router(responses_router.router)
app.include_router(participants_router.router)
app.include_router(results_router.router)
app.include_router(share_router.router)
app.include_router(quiz_router.router)
app.include_router(report_router.router)
app.include_router(reporting_router.router)
app.include_router(og_router.router)
app.include_router(couple_router.router)
app.include_router(invites_router.router)
app.include_router(profile_router.router)

if hasattr(share_router, "limiter"):
    app.state.limiter = share_router.limiter


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid4()))
    request.state.request_id = request_id
    token = bind_request_id(request_id)
    try:
        response = await call_next(request)
    except ProblemDetailsException as exc:
        response = from_exception(request, exc)
    except RequestValidationError as exc:
        log.warning(
            "Validation error",
            extra={
                "request_id": request_id,
                "errors": exc.errors(),
            },
        )
        response = from_validation_error(request, exc)
    except HTTPException as exc:
        response = from_http_exception(request, exc)
    except Exception:
        log.exception(
            "Unhandled application error",
            extra={"request_id": request_id},
        )
        response = internal_server_error(request)
    finally:
        reset_request_id(token)
    response.headers[REQUEST_ID_HEADER] = request_id
    if trace:
        span = trace.get_current_span()
        if span and span.is_recording():
            span.set_attribute("http.request_id", request_id)
    if response.status_code == 404 and request.scope.get("endpoint") is None:
        override = problem_response(
            request,
            status=404,
            title="Not Found",
            detail="Not Found",
            type_suffix="http-404",
        )
        override.headers[REQUEST_ID_HEADER] = request_id
        return override
    return response


if RateLimitExceeded:  # pragma: no cover - optional dependency

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
        detail = getattr(exc, "detail", "요청 한도를 초과했습니다.")
        response = problem_response(
            request,
            status=429,
            title="Rate Limit Exceeded",
            detail=detail,
            type_suffix="rate-limit",
        )
        headers = dict(getattr(exc, "headers", {}) or {})
        if "Retry-After" not in headers:
            limiter = getattr(request.app.state, "limiter", None)
            limit_info = getattr(request.state, "view_rate_limit", None)
            if limiter and limit_info:
                limit_item, limit_args = limit_info
                try:
                    window_stats = limiter.limiter.get_window_stats(
                        limit_item, *limit_args
                    )
                    reset_in = 1 + window_stats[0]
                    if getattr(limiter, "_retry_after", None) == "http-date":
                        headers["Retry-After"] = formatdate(reset_in)
                    else:
                        headers["Retry-After"] = str(
                            max(0, int(reset_in - time.time()))
                        )
                except Exception:
                    pass
        for key, value in headers.items():
            response.headers[key] = value
        return response


@app.exception_handler(ProblemDetailsException)
async def problem_details_handler(request: Request, exc: ProblemDetailsException):
    return from_exception(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    log.warning(
        "Validation error",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "errors": exc.errors(),
        },
    )
    return from_validation_error(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc, ProblemDetailsException):
        return from_exception(request, exc)
    return from_http_exception(request, exc)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.exception(
        "Unhandled application error",
        extra={"request_id": getattr(request.state, "request_id", None)},
    )
    return internal_server_error(request)


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    with session_scope() as db:
        seed_questions(db)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("mbti/index.html", {"request": request})

@app.get("/mbti", response_class=HTMLResponse)
async def mbti_landing(request: Request):
    return templates.TemplateResponse("mbti/index.html", {"request": request})

@app.get("/mbti/self-test", response_class=HTMLResponse)
async def mbti_self_test(request: Request):
    questions = _build_questions("basic", perspective="self")
    return templates.TemplateResponse("mbti/self_test.html", {"request": request, "questions": questions})

@app.get("/mbti/friend", response_class=HTMLResponse)
async def mbti_friend(
    request: Request,
    prefill_name: str | None = None,
    prefill_mbti: str | None = None,
):
    response = templates.TemplateResponse(
        "mbti/friend_input.html",
        {
            "request": request,
            "prefill_name": prefill_name or "",
            "prefill_mbti": prefill_mbti or "",
            "owner_avatar": None,
            "robots_meta": NOINDEX_VALUE,
        },
    )
    apply_noindex_headers(response)
    return response


@app.post("/mbti/friend", response_class=HTMLResponse)
async def submit_friend(request: Request):
    form = await request.form()

    invite_token = (form.get("invite_token") or "").strip()
    friend_name = (form.get("friend_name") or "").strip() or "친구"
    friend_mbti = (form.get("friend_mbti") or "").strip()
    relation_value = (form.get("relationship") or "").strip()
    responder_name = (form.get("responder_name") or "").strip()

    relation_label = RELATION_LABELS.get(relation_value, relation_value or "")

    registration = None
    if invite_token:
        if not relation_value:
            raise HTTPException(status_code=400, detail="관계를 선택해 주세요.")

        try:
            ParticipantRelation(relation_value)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="지원하지 않는 관계입니다.") from exc

        registration_payload = ParticipantRegistrationRequest(
            relation=relation_value,
            display_name=responder_name or None,
            consent_display=False,
        )

        with session_scope() as db:
            registration = await register_participant(
                invite_token=invite_token,
                payload=registration_payload,
                db=db,
            )

        responder_name = registration.display_name

    friend_info = {
        "name": friend_name,
        "mbti": friend_mbti,
        "relationship": relation_value,
        "relation_label": relation_label,
        "responder_name": responder_name,
        "participant_id": registration.participant_id if registration else None,
        "session_id": registration.session_id if registration else None,
        "invite_token": invite_token,
    }

    questions = _build_questions("friend", perspective="other")
    response = templates.TemplateResponse(
        "mbti/test.html",
        {
            "request": request,
            "questions": questions,
            "friend_info": friend_info,
        },
    )
    apply_noindex_headers(response)
    return response


@app.get("/mbti/test", response_class=HTMLResponse)
async def mbti_test(
    request: Request,
    friend_name: str | None = None,
    friend_mbti: str | None = None,
    relationship: str | None = None,
    responder_name: str | None = None,
):
    questions = _build_questions("friend", perspective="other")
    friend_info = None
    if friend_name or friend_mbti or relationship or responder_name:
        friend_info = {
            "name": friend_name or "",
            "mbti": friend_mbti or "",
            "relationship": relationship or "",
            "responder_name": responder_name or "",
        }
    return templates.TemplateResponse(
        "mbti/test.html",
        {
            "request": request,
            "questions": questions,
            "friend_info": friend_info,
        },
    )


@app.post("/mbti/self-result", response_class=HTMLResponse)
async def mbti_self_result(request: Request):
    form = await request.form()
    answer_pairs = []
    for key, value in form.items():
        if not key.startswith("q"):
            continue
        try:
            question_id = int(key[1:])
            answer_value = int(value)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail="Invalid answer payload") from exc
        answer_pairs.append((question_id, answer_value))

    try:
        mbti_type, scores, _ = _score_answers(answer_pairs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = MBTI_SUMMARIES.get(mbti_type, _DEFAULT_SUMMARY)

    response = templates.TemplateResponse(
        "mbti/self_result.html",
        {
            "request": request,
            "mbti_type": mbti_type,
            "scores": scores,
            "result": result,
            "robots_meta": NOINDEX_VALUE,
        },
    )
    apply_noindex_headers(response)
    return response


@app.post("/mbti/result", response_class=HTMLResponse)
async def mbti_result(request: Request):
    form = await request.form()
    answer_pairs = []
    for key, value in form.items():
        if not key.startswith("q"):
            continue
        try:
            question_id = int(key[1:])
            answer_value = int(value)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail="Invalid answer payload") from exc
        answer_pairs.append((question_id, answer_value))

    try:
        mbti_type, scores, _ = _score_answers(answer_pairs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = MBTI_SUMMARIES.get(mbti_type, _DEFAULT_SUMMARY)

    friend_name = (form.get("friend_name") or "").strip()
    friend_relationship = (form.get("relationship") or "").strip()
    responder_name = (form.get("responder_name") or "").strip()
    friend_mbti = (form.get("friend_mbti") or "").strip()

    response = templates.TemplateResponse(
        "mbti/result.html",
        {
            "request": request,
            "mbti_type": mbti_type,
            "scores": scores,
            "result": result,
            "pair_token": None,
            "robots_meta": NOINDEX_VALUE,
            "friend_name": friend_name or None,
            "friend_relationship": friend_relationship or None,
            "responder_name": responder_name or None,
            "friend_mbti": friend_mbti or None,
        },
    )
    apply_noindex_headers(response)
    return response


@app.post("/mbti/result/{token}", response_class=HTMLResponse)
async def mbti_friend_result(request: Request, token: str):
    """친구 테스트 결과 제출 (토큰 기반)"""
    try:
        from app.core.token import verify_token
        pair_id, my_mbti = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
    # 데이터베이스에서 친구 정보 가져오기
    from app.core.db import get_session
    from app.core.models_db import Pair
    session = next(get_session())
    pair = session.get(Pair, pair_id)
    if not pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    
    form = await request.form()
    answer_pairs = []
    for key, value in form.items():
        if not key.startswith("q"):
            continue
        try:
            question_id = int(key[1:])
            answer_value = int(value)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail="Invalid answer payload") from exc
        answer_pairs.append((question_id, answer_value))

    try:
        mbti_type, scores, _ = _score_answers(answer_pairs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = MBTI_SUMMARIES.get(mbti_type, _DEFAULT_SUMMARY)

    # 친구 정보 구성
    friend_info = {
        "name": pair.my_name or "",
        "display_name": pair.my_name or "",
        "show_public": pair.show_public,
        "avatar": pair.my_avatar,
        "mbti": my_mbti or (pair.my_mbti or ""),
    }

    # 통계 정보 구성 (기본값)
    statistics = {
        "total_evaluations": 1,
        "average_score": 50.0,
        "mbti_distribution": {
            mbti_type: 1
        },
        "average_scores": {
            "E": scores.get("E", 50),
            "I": scores.get("I", 50),
            "S": scores.get("S", 50),
            "N": scores.get("N", 50),
            "T": scores.get("T", 50),
            "F": scores.get("F", 50),
            "J": scores.get("J", 50),
            "P": scores.get("P", 50)
        }
    }

    invite_url = build_invite_url(request, token)

    response = templates.TemplateResponse(
        "mbti/friend_results.html",
        {
            "request": request,
            "mbti_type": mbti_type,
            "scores": scores,
            "result": result,
            "my_mbti": my_mbti,
            "friend_info": friend_info,
            "statistics": statistics,
            "invite_url": invite_url,
            "robots_meta": NOINDEX_VALUE,
        },
    )
    apply_noindex_headers(response)
    return response


@app.get("/mbti/types", response_class=HTMLResponse)
async def mbti_types(request: Request):
    ordered = sorted(MBTI_SUMMARIES.items(), key=lambda item: item[0])
    return templates.TemplateResponse(
        "mbti/types.html",
        {
            "request": request,
            "summaries": ordered,
        },
    )


@app.get("/mbti/friend-system", response_class=HTMLResponse)
async def mbti_friend_system(request: Request):
    return templates.TemplateResponse("mbti/friend_system.html", {"request": request})


@app.get("/mbti/share", response_class=HTMLResponse)
async def mbti_share(
    request: Request,
    name: str | None = None,
    mbti: str | None = None,
):
    response = templates.TemplateResponse(
        "mbti/share.html",
        {
            "request": request,
            "name": name,
            "mbti": mbti,
            "robots_meta": NOINDEX_VALUE,
        },
    )
    apply_noindex_headers(response)
    return response


@app.get("/mbti/share_success", response_class=HTMLResponse)
async def mbti_share_success(
    request: Request,
    url: str | None = None,
    name: str | None = None,
    mbti: str | None = None,
):
    response = templates.TemplateResponse(
        "mbti/share_success.html",
        {
            "request": request,
            "url": url,
            "name": name,
            "mbti": mbti,
            "robots_meta": NOINDEX_VALUE,
        },
    )
    apply_noindex_headers(response)
    return response


@app.get("/i/{token}", response_class=HTMLResponse, name="invite_public")
def invite_public(
    request: Request,
    token: str,
    session=Depends(get_core_session),
    db: OrmSession = Depends(get_db),
):
    session_record = (
        db.query(SessionModel)
        .filter(SessionModel.invite_token == token)
        .one_or_none()
    )

    if session_record is not None:
        now = datetime.now(timezone.utc)
        expires_at = session_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now:
            owner_name = session_record.snapshot_owner_name or "초대한 분"
            return problem_response(
                request,
                status=410,
                title="Invite Expired",
                detail=f"초대가 만료되었어요. {owner_name}님께 새 링크를 요청해 주세요.",
                type_suffix="invite-expired",
            )

        respondent_count = (
            db.query(Participant)
            .filter(Participant.session_id == session_record.id)
            .count()
        )

        if respondent_count >= session_record.max_raters:
            return problem_response(
                request,
                status=429,
                title="Invite Capacity Reached",
                detail="참여 인원이 모두 모였어요. 관심에 감사드립니다!",
                type_suffix="invite-capacity",
            )

        response = templates.TemplateResponse(
            "mbti/friend_input.html",
            {
                "request": request,
                "prefill_name": session_record.snapshot_owner_name or "",
                "prefill_mbti": session_record.self_mbti or "",
                "owner_avatar": session_record.snapshot_owner_avatar or "",
                "invite_token": token,
                "robots_meta": NOINDEX_VALUE,
            },
        )
        apply_noindex_headers(response)
        return response

    return quiz_router.render_invite_page(request, token, session)

@app.get("/api", tags=["system"])
async def api_root():
    return {"service": "perception-gap", "status": "online"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
try:  # pragma: no cover - optional dependency
    from slowapi.errors import RateLimitExceeded  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    RateLimitExceeded = None  # type: ignore[assignment]
