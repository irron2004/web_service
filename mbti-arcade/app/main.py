from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI, Request

from app.core.config import REQUEST_ID_HEADER
from app.data.loader import seed_questions
from app.database import Base, engine, session_scope
from app.routers import health
from app.routers import responses as responses_router
from app.routers import results as results_router
from app.routers import sessions as sessions_router
from app.utils.problem_details import ProblemDetailsException, from_exception

log = logging.getLogger("perception_gap")

app = FastAPI(
    title="360Me Perception Gap Service",
    description="Self vs Others perception gap scoring with RFC 9457 errors and observability hooks.",
    version="0.9.0",
)

app.include_router(health.router)
app.include_router(sessions_router.router)
app.include_router(responses_router.router)
app.include_router(results_router.router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response


@app.exception_handler(ProblemDetailsException)
async def problem_details_handler(request: Request, exc: ProblemDetailsException):
    return from_exception(request, exc)


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    with session_scope() as db:
        seed_questions(db)


@app.get("/", tags=["system"])
async def root():
    return {"service": "perception-gap", "status": "online"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
