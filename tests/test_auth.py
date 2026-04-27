"""
Tests for authentication service.
Uses in-memory SQLite, no real DB file created.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    decode_token,
    register_user,
)


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    from app import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestRegister:
    def test_register_creates_user(self, db):
        user = register_user(db, "alice", "password123")
        assert user.id
        assert user.username == "alice"
        assert user.hashed_password != "password123"

    def test_duplicate_username_raises(self, db):
        register_user(db, "alice", "password123")
        with pytest.raises(ValueError, match="already exists"):
            register_user(db, "alice", "other")


class TestAuthenticate:
    def test_valid_credentials(self, db):
        register_user(db, "bob", "mypassword")
        user = authenticate_user(db, "bob", "mypassword")
        assert user is not None
        assert user.username == "bob"

    def test_wrong_password(self, db):
        register_user(db, "bob", "mypassword")
        user = authenticate_user(db, "bob", "wrong")
        assert user is None

    def test_unknown_user(self, db):
        user = authenticate_user(db, "nobody", "pass")
        assert user is None


class TestJWT:
    def test_create_and_decode_token(self, db):
        user = register_user(db, "charlie", "pass123")
        token = create_access_token(user.id)
        decoded_id = decode_token(token)
        assert decoded_id == user.id

    def test_invalid_token_returns_none(self):
        assert decode_token("notavalidtoken") is None

    def test_tampered_token_returns_none(self, db):
        user = register_user(db, "dave", "pass123")
        token = create_access_token(user.id)
        tampered = token[:-4] + "XXXX"
        assert decode_token(tampered) is None
