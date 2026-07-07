import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.infrastructure.database import Base, engine, SessionLocal
from app.models.models import SyncedSubmission, SyncJob, SyncLog
from app.models.schemas import SyncedSubmissionResponse, SyncJobResponse, SyncLogResponse

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create all tables in sqlite
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after testing
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_synced_submission_crud(db_session: Session):
    # Create
    new_submission = SyncedSubmission(
        leetcode_submission_id="123456",
        problem_id="1",
        problem_title="Two Sum",
        difficulty="Easy",
        language="python3",
        topic_tags="Array,Hash Table",
        solved_at=datetime.utcnow(),
        github_commit_sha="abc123sha",
        github_file_path="leetcode/Easy/Arrays/0001_Two_Sum/solution.py"
    )
    db_session.add(new_submission)
    db_session.commit()
    db_session.refresh(new_submission)

    # Read and verify
    queried = db_session.query(SyncedSubmission).filter_by(leetcode_submission_id="123456").first()
    assert queried is not None
    assert queried.problem_title == "Two Sum"
    assert queried.difficulty == "Easy"

    # Schema serialization
    response_schema = SyncedSubmissionResponse.model_validate(queried)
    assert response_schema.leetcode_submission_id == "123456"
    assert response_schema.problem_title == "Two Sum"

def test_sync_job_crud(db_session: Session):
    # Create
    job = SyncJob(status="RUNNING")
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Update
    job.status = "COMPLETED"
    job.end_time = datetime.utcnow()
    job.execution_time_seconds = 1.25
    db_session.commit()

    # Verify
    queried = db_session.query(SyncJob).filter_by(id=job.id).first()
    assert queried is not None
    assert queried.status == "COMPLETED"
    assert queried.execution_time_seconds == 1.25

    # Schema serialization
    response = SyncJobResponse.model_validate(queried)
    assert response.status == "COMPLETED"

def test_sync_log_crud(db_session: Session):
    # Create
    log = SyncLog(
        level="ERROR",
        message="Failed to connect to GitHub API",
        error_code="GITHUB_API_ERROR",
        recovery_suggestion="Check network status and verify your GitHub Token configuration"
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    # Verify
    queried = db_session.query(SyncLog).filter_by(id=log.id).first()
    assert queried is not None
    assert queried.level == "ERROR"
    assert queried.error_code == "GITHUB_API_ERROR"

    # Schema serialization
    response = SyncLogResponse.model_validate(queried)
    assert response.level == "ERROR"
