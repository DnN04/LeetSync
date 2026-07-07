from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database import Base

class SyncedSubmission(Base):
    __tablename__ = "synced_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    leetcode_submission_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    problem_id: Mapped[str] = mapped_column(String(50), index=True)
    problem_title: Mapped[str] = mapped_column(String(255))
    difficulty: Mapped[str] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(50))
    topic_tags: Mapped[str] = mapped_column(String(500))  # Comma-separated topic tags
    solved_at: Mapped[datetime] = mapped_column(DateTime)
    github_commit_sha: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    github_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING")  # RUNNING, COMPLETED, FAILED
    execution_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    level: Mapped[str] = mapped_column(String(50))  # INFO, WARNING, ERROR
    message: Mapped[str] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recovery_suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
