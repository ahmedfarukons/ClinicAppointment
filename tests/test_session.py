"""
Tests for session service.
Uses in-memory SQLite.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.auth_service import register_user
from app.services.session_service import (
    add_message,
    create_session,
    delete_session,
    get_history,
    get_session,
    list_sessions,
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


@pytest.fixture
def user(db):
    return register_user(db, "testuser", "testpass")


class TestSessionService:
    def test_create_session(self, db, user):
        sess = create_session(db, user.id)
        assert sess.id
        assert sess.user_id == user.id
        assert sess.title == "New Chat"

    def test_list_sessions(self, db, user):
        create_session(db, user.id, "First")
        create_session(db, user.id, "Second")
        sessions = list_sessions(db, user.id)
        assert len(sessions) == 2

    def test_get_session(self, db, user):
        sess = create_session(db, user.id)
        found = get_session(db, sess.id)
        assert found is not None
        assert found.id == sess.id

    def test_get_session_not_found(self, db, user):
        found = get_session(db, "nonexistent")
        assert found is None

    def test_add_message(self, db, user):
        sess = create_session(db, user.id)
        msg = add_message(db, sess.id, role="user", content="Hello")
        assert msg.id
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_session_title_from_first_message(self, db, user):
        sess = create_session(db, user.id)
        add_message(db, sess.id, role="user", content="What is diabetes?")
        updated = get_session(db, sess.id)
        assert "diabetes" in updated.title.lower()

    def test_get_history(self, db, user):
        sess = create_session(db, user.id)
        add_message(db, sess.id, role="user", content="Q1")
        add_message(db, sess.id, role="assistant", content="A1")
        add_message(db, sess.id, role="user", content="Q2")
        history = get_history(db, sess.id)
        assert len(history) == 3
        assert history[0].content == "Q1"
        assert history[-1].content == "Q2"

    def test_delete_session(self, db, user):
        sess = create_session(db, user.id)
        result = delete_session(db, sess.id)
        assert result is True
        assert get_session(db, sess.id) is None

    def test_delete_nonexistent_session(self, db, user):
        result = delete_session(db, "ghost_id")
        assert result is False
