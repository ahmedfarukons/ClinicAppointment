"""
FastAPI application entry point.

Includes:
- Structured logging
- Request logging middleware
- Rate limiting
- Auth endpoints (register / login)
- Session management endpoints
- Chat endpoint
- Static file serving (frontend)
"""

from __future__ import annotations

import os
from typing import Annotated

import structlog
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.middleware.rate_limiter import limiter
from app.models import (
    ChatRequest,
    ChatResponse,
    LoginRequest,
    MessageInfo,
    RegisterRequest,
    SessionInfo,
    TokenResponse,
)
from app.services import auth_service, session_service
from app.services.orchestrator import run_pipeline

# ── Logging setup ─────────────────────────────────────────────────────────────
setup_logging(settings.log_level)
logger = structlog.get_logger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ChatDoctor Clinical Assistant",
    description="Intent Router + RAG + Appointment Agent + XAI",
    version="2.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestLoggingMiddleware)


# ── Auth dependency ────────────────────────────────────────────────────────────
def _current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> str:
    """Resolve Bearer token → user_id. Raises 401 if invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.removeprefix("Bearer ").strip()
    user_id = auth_service.decode_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = auth_service.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user_id


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup() -> None:
    os.makedirs("data", exist_ok=True)
    init_db()
    logger.info("app_started", version="2.0.0")


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0"}


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/auth/register", response_model=TokenResponse, tags=["Auth"])
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        user = auth_service.register_user(db, payload.username, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    token = auth_service.create_access_token(user.id)
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token(user.id)
    return TokenResponse(access_token=token)


# ── Sessions ──────────────────────────────────────────────────────────────────
@app.get("/sessions", response_model=list[SessionInfo], tags=["Sessions"])
def list_sessions(
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
) -> list[SessionInfo]:
    rows = session_service.list_sessions(db, user_id)
    return [
        SessionInfo(
            id=r.id,
            title=r.title,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]


@app.post("/sessions", response_model=SessionInfo, tags=["Sessions"])
def create_session(
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
) -> SessionInfo:
    row = session_service.create_session(db, user_id)
    return SessionInfo(
        id=row.id,
        title=row.title,
        created_at=row.created_at.isoformat(),
        updated_at=row.updated_at.isoformat(),
    )


@app.get("/sessions/{session_id}/messages", response_model=list[MessageInfo], tags=["Sessions"])
def get_messages(
    session_id: str,
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
) -> list[MessageInfo]:
    sess = session_service.get_session(db, session_id)
    if not sess or sess.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = session_service.get_history(db, session_id)
    return [
        MessageInfo(
            id=m.id,
            role=m.role,
            content=m.content,
            route=m.route,
            created_at=m.created_at.isoformat(),
        )
        for m in msgs
    ]


@app.delete("/sessions/{session_id}", tags=["Sessions"])
def delete_session(
    session_id: str,
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    sess = session_service.get_session(db, session_id)
    if not sess or sess.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    session_service.delete_session(db, session_id)
    return {"status": "deleted"}


# ── Chat ──────────────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
@limiter.limit(settings.rate_limit)
def chat(
    request: Request,
    payload: ChatRequest,
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
) -> ChatResponse:
    # Resolve or create session
    sid = payload.session_id
    if sid:
        sess = session_service.get_session(db, sid)
        if not sess or sess.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        sess = session_service.create_session(db, user_id)
        sid = sess.id

    # Persist user message
    session_service.add_message(db, sid, role="user", content=payload.message)

    # Run pipeline
    result = run_pipeline(message=payload.message, session_id=sid)

    # Persist assistant message
    session_service.add_message(
        db, sid,
        role="assistant",
        content=result.answer,
        route=result.route,
        xai=result.xai.model_dump(),
    )

    return result


# ── Static files (Frontend) ───────────────────────────────────────────────────
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        return FileResponse(os.path.join(_static_dir, "index.html"))
