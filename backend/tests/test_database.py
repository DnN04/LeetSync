import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.infrastructure.database import Base, engine, get_db, SessionLocal

def test_database_connection():
    # Verify we can connect to the database and run a simple query
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1

def test_get_db_session():
    # Verify get_db yields a valid Session object and closes it
    db_gen = get_db()
    db = next(db_gen)
    try:
        assert isinstance(db, Session)
        # Check active session context
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        # Close session by continuing generator
        try:
            next(db_gen)
        except StopIteration:
            pass

def test_session_local():
    session = SessionLocal()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()
