from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# Synced Submission Schemas
class SyncedSubmissionBase(BaseModel):
    leetcode_submission_id: str
    problem_id: str
    problem_title: str
    difficulty: str
    language: str
    topic_tags: str
    solved_at: datetime
    github_commit_sha: Optional[str] = None
    github_file_path: Optional[str] = None

class SyncedSubmissionCreate(SyncedSubmissionBase):
    pass

class SyncedSubmissionResponse(SyncedSubmissionBase):
    id: int
    synced_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Sync Job Schemas
class SyncJobBase(BaseModel):
    status: str
    error_message: Optional[str] = None

class SyncJobCreate(BaseModel):
    start_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = "RUNNING"

class SyncJobUpdate(BaseModel):
    end_time: datetime = Field(default_factory=datetime.utcnow)
    status: str
    execution_time_seconds: float
    error_message: Optional[str] = None

class SyncJobResponse(SyncJobBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# Sync Log Schemas
class SyncLogBase(BaseModel):
    level: str
    message: str
    error_code: Optional[str] = None
    recovery_suggestion: Optional[str] = None

class SyncLogCreate(SyncLogBase):
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SyncLogResponse(SyncLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
