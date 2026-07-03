from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.config.settings import settings

# In SQLAlchemy 2.0, subclass DeclarativeBase to create base model class
class Base(DeclarativeBase):
    pass

# Create engine
# For SQLite, ensure we allow multithreaded access for development API integration
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

def init_db() -> None:
    """Initializes the database schema by creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency generator for database sessions.
    
    Yields:
        Session: Active SQLAlchemy session database context.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
