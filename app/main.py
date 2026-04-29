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
from app.db_models import AppointmentRow
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
    UserProfile,
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


@app.get("/auth/me", response_model=UserProfile, tags=["Auth"])
def current_user_profile(
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
) -> UserProfile:
    user = auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserProfile(
        id=user.id,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        session_count=len(session_service.list_sessions(db, user_id)),
        appointment_count=db.query(AppointmentRow).filter(AppointmentRow.user_id == user_id).count(),
    )


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


# ── Appointments ──────────────────────────────────────────────────────────────
from app.models import (
    AdminLoginRequest, AdminStats, AdminTokenResponse,
    AppointmentCreate, AppointmentResponse, AppointmentStatusUpdate,
)
from datetime import date as _date, timedelta
import hmac, hashlib, json as _json


def _make_admin_token() -> str:
    import time, base64
    payload = _json.dumps({"role": "admin", "exp": int(time.time()) + 86400 * 7})
    sig = hmac.new(settings.jwt_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.b64encode(f"{payload}.{sig}".encode()).decode()


def _verify_admin_token(authorization: str | None) -> bool:
    if not authorization or not authorization.startswith("Bearer "):
        return False
    import base64, time
    try:
        raw = base64.b64decode(authorization.removeprefix("Bearer ").strip()).decode()
        payload_str, sig = raw.rsplit(".", 1)
        expected = hmac.new(settings.jwt_secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        payload = _json.loads(payload_str)
        return payload.get("role") == "admin" and payload.get("exp", 0) > time.time()
    except Exception:
        return False


def _admin_guard(authorization: Annotated[str | None, Header()] = None) -> None:
    if not _verify_admin_token(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin token required")


def _row_to_response(r: AppointmentRow) -> AppointmentResponse:
    return AppointmentResponse(
        id=r.id,
        patient_name=r.patient_name,
        phone=r.phone,
        date=r.date,
        time=r.time,
        department=r.department,
        doctor=r.doctor,
        status=r.status,
        created_at=r.created_at.isoformat(),
    )


# ── Public Appointments ───────────────────────────────────────────────────────
@app.get("/api/appointments", response_model=list[AppointmentResponse], tags=["Appointments"])
def get_appointments(
    date: str | None = None,
    department: str | None = None,
    doctor: str | None = None,
    db: Session = Depends(get_db),
) -> list[AppointmentResponse]:
    query = db.query(AppointmentRow)
    if date:
        query = query.filter(AppointmentRow.date == date)
    if department:
        query = query.filter(AppointmentRow.department == department)
    if doctor:
        query = query.filter(AppointmentRow.doctor == doctor)
    return [_row_to_response(r) for r in query.all()]


@app.post("/api/appointments", response_model=AppointmentResponse, tags=["Appointments"])
def create_appointment(
    payload: AppointmentCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    existing = db.query(AppointmentRow).filter(
        AppointmentRow.date == payload.date,
        AppointmentRow.time == payload.time,
        AppointmentRow.doctor == payload.doctor,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This doctor is already booked at this time. Please choose another time or doctor.")

    user_id = None
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
        user_id = auth_service.decode_token(token)

    row = AppointmentRow(
        user_id=user_id,
        patient_name=payload.patient_name,
        phone=payload.phone,
        date=payload.date,
        time=payload.time,
        department=payload.department,
        doctor=payload.doctor,
        status="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_response(row)


# ── Admin Auth ────────────────────────────────────────────────────────────────
@app.post("/admin/login", response_model=AdminTokenResponse, tags=["Admin"])
def admin_login(payload: AdminLoginRequest) -> AdminTokenResponse:
    admin_user = os.environ.get("ADMIN_USERNAME", "admin")
    admin_pass = os.environ.get("ADMIN_PASSWORD", "clinic2024")
    if payload.username != admin_user or payload.password != admin_pass:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials")
    return AdminTokenResponse(access_token=_make_admin_token())


# ── Admin Stats ───────────────────────────────────────────────────────────────
@app.get("/admin/stats", response_model=AdminStats, tags=["Admin"])
def admin_stats(
    _: None = Depends(_admin_guard),
    db: Session = Depends(get_db),
) -> AdminStats:
    all_rows = db.query(AppointmentRow).all()
    today_str = _date.today().isoformat()
    week_start = (_date.today() - timedelta(days=_date.today().weekday())).isoformat()

    by_dept: dict[str, int] = {}
    by_status: dict[str, int] = {}
    today_count = 0
    week_count = 0

    for r in all_rows:
        dept = r.department or "Other"
        by_dept[dept] = by_dept.get(dept, 0) + 1
        st = r.status or "pending"
        by_status[st] = by_status.get(st, 0) + 1
        if r.date == today_str:
            today_count += 1
        if r.date >= week_start:
            week_count += 1

    return AdminStats(
        total=len(all_rows),
        today=today_count,
        this_week=week_count,
        by_department=by_dept,
        by_status=by_status,
    )


# ── Admin Appointments ────────────────────────────────────────────────────────
@app.get("/admin/appointments", response_model=list[AppointmentResponse], tags=["Admin"])
def admin_list_appointments(
    date: str | None = None,
    department: str | None = None,
    doctor: str | None = None,
    search: str | None = None,
    appt_status: str | None = None,
    _: None = Depends(_admin_guard),
    db: Session = Depends(get_db),
) -> list[AppointmentResponse]:
    query = db.query(AppointmentRow)
    if date:
        query = query.filter(AppointmentRow.date == date)
    if department:
        query = query.filter(AppointmentRow.department == department)
    if doctor:
        query = query.filter(AppointmentRow.doctor == doctor)
    if appt_status:
        query = query.filter(AppointmentRow.status == appt_status)
    rows = query.order_by(AppointmentRow.date.asc(), AppointmentRow.time.asc()).all()
    if search:
        s = search.lower()
        rows = [r for r in rows if s in r.patient_name.lower() or s in (r.phone or "")]
    return [_row_to_response(r) for r in rows]


@app.patch("/admin/appointments/{appt_id}/status", response_model=AppointmentResponse, tags=["Admin"])
def admin_update_status(
    appt_id: str,
    payload: AppointmentStatusUpdate,
    _: None = Depends(_admin_guard),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    if payload.status not in ("pending", "confirmed", "cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status value")
    row = db.query(AppointmentRow).filter(AppointmentRow.id == appt_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")
    row.status = payload.status
    db.commit()
    db.refresh(row)
    return _row_to_response(row)


@app.delete("/admin/appointments/{appt_id}", tags=["Admin"])
def admin_delete_appointment(
    appt_id: str,
    _: None = Depends(_admin_guard),
    db: Session = Depends(get_db),
) -> dict:
    row = db.query(AppointmentRow).filter(AppointmentRow.id == appt_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(row)
    db.commit()
    return {"status": "deleted", "id": appt_id}


# ── Static files (Frontend) ───────────────────────────────────────────────────
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_index(full_path: str) -> FileResponse:
        # Eğer istek bir API veya static dosya değilse index.html döndür
        if full_path.startswith("api/") or full_path.startswith("admin/") or full_path.startswith("static/"):
             # Bunlar zaten kendi handler'larına sahip, buraya girerse 404'tür ama
             # React Router için /admin/login gibi adresleri korumalıyız
             pass
        return FileResponse(os.path.join(_static_dir, "index.html"))


