"""
Session & message persistence service.

Provides CRUD operations for chat sessions and message history.
"""

from __future__ import annotations

import json
from typing import Optional

import structlog
from sqlalchemy.orm import Session

from app.db_models import MessageRow, SessionRow

logger = structlog.get_logger(__name__)


def create_session(db: Session, user_id: str, title: str = "New Chat") -> SessionRow:
    """Create a new chat session for the given user."""
    row = SessionRow(user_id=user_id, title=title)
    db.add(row)
    db.commit()
    db.refresh(row)
    logger.info("session_created", session_id=row.id, user_id=user_id)
    return row


def list_sessions(db: Session, user_id: str) -> list[SessionRow]:
    """Return all sessions for a user, newest first."""
    return (
        db.query(SessionRow)
        .filter(SessionRow.user_id == user_id)
        .order_by(SessionRow.updated_at.desc())
        .all()
    )


def get_session(db: Session, session_id: str) -> Optional[SessionRow]:
    """Return a single session or None."""
    return db.query(SessionRow).filter(SessionRow.id == session_id).first()


def add_message(
    db: Session,
    session_id: str,
    role: str,
    content: str,
    route: str | None = None,
    xai: dict | None = None,
) -> MessageRow:
    """Append a message to a session."""
    xai_str = json.dumps(xai) if xai else None
    msg = MessageRow(
        session_id=session_id,
        role=role,
        content=content,
        route=route,
        xai_json=xai_str,
    )
    db.add(msg)

    # Update session timestamp
    session = db.query(SessionRow).filter(SessionRow.id == session_id).first()
    if session:
        from datetime import datetime, timezone
        session.updated_at = datetime.now(timezone.utc)
        # Auto-title from first user message
        if role == "user" and session.title == "New Chat":
            session.title = content[:80]

    db.commit()
    db.refresh(msg)
    return msg


def get_history(db: Session, session_id: str, limit: int = 20) -> list[MessageRow]:
    """Return the last N messages in a session, oldest first."""
    msgs = (
        db.query(MessageRow)
        .filter(MessageRow.session_id == session_id)
        .order_by(MessageRow.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(msgs))


def delete_session(db: Session, session_id: str) -> bool:
    """Delete a session and all its messages."""
    session = db.query(SessionRow).filter(SessionRow.id == session_id).first()
    if not session:
        return False
    db.delete(session)
    db.commit()
    logger.info("session_deleted", session_id=session_id)
    return True
