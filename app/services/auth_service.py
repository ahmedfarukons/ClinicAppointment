"""
Authentication service — registration, login, JWT token management.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import structlog
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.db_models import UserRow

logger = structlog.get_logger(__name__)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def register_user(db: Session, username: str, password: str) -> UserRow:
    """Create a new user. Raises ValueError if username is taken."""
    existing = db.query(UserRow).filter(UserRow.username == username).first()
    if existing:
        raise ValueError("Username already exists")

    user = UserRow(
        username=username,
        hashed_password=_hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("user_registered", user_id=user.id, username=username)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserRow]:
    """Return the user if credentials are valid, else None."""
    user = db.query(UserRow).filter(UserRow.username == username).first()
    if not user or not _verify_password(password, user.hashed_password):
        logger.warning("login_failed", username=username)
        return None
    logger.info("user_authenticated", user_id=user.id)
    return user


def create_access_token(user_id: str) -> str:
    """Create a JWT access token for the given user."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[str]:
    """Decode a JWT token and return user_id, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except JWTError:
        return None


def get_user_by_id(db: Session, user_id: str) -> Optional[UserRow]:
    """Look up a user by their ID."""
    return db.query(UserRow).filter(UserRow.id == user_id).first()
