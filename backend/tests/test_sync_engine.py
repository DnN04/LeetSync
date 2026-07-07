from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.infrastructure.database import Base
from app.models.models import SyncedSubmission, SyncJob, SyncLog
from app.services.sync_engine import SyncEngineService
from app.integrations.github import GitHubIntegration
from app.integrations.leetcode import LeetCodeIntegration

@pytest.fixture(name="db_session")
def fixture_db_session() -> Session:
    # Set up in-memory sqlite database for the sync engine tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionClass = sessionmaker(bind=engine)
    session = SessionClass()
    yield session
    session.close()

def test_sync_engine_formatting():
    service = SyncEngineService(github_client=MagicMock(), leetcode_client=MagicMock())
    assert service.get_extension("Python3") == "py"
    assert service.get_extension("Java") == "java"
    assert service.get_extension("custom-lang") == "txt"
    
    assert service.format_title_slug("1", "two-sum") == "0001_Two_Sum"
    assert service.format_title_slug("123", "binary-tree-maximum-path-sum") == "0123_Binary_Tree_Maximum_Path_Sum"
    
    tags = [{"name": "Array", "slug": "array"}]
    assert service.get_primary_topic(tags) == "Arrays"
    assert service.get_primary_topic([]) == "Algorithms"

def test_sync_engine_run_completed_no_new_submissions(db_session: Session):
    mock_gh = MagicMock(spec=GitHubIntegration)
    mock_gh.validate_credentials.return_value = True
    
    mock_lc = MagicMock(spec=LeetCodeIntegration)
    mock_lc.validate_session.return_value = True
    # Return empty recent submissions
    mock_lc.get_recent_accepted_submissions.return_value = []

    service = SyncEngineService(github_client=mock_gh, leetcode_client=mock_lc)
    job = service.run_sync(db_session)
    
    assert job.status == "COMPLETED"
    assert job.error_message is None
    
    # Check that a SyncJob is saved in db
    db_job = db_session.query(SyncJob).filter_by(id=job.id).first()
    assert db_job is not None
    assert db_job.status == "COMPLETED"
    
    # Check that log is created
    log = db_session.query(SyncLog).first()
    assert log is not None
    assert "completed successfully" in log.message

def test_sync_engine_run_synchronizes_new_submissions(db_session: Session):
    mock_gh = MagicMock(spec=GitHubIntegration)
    mock_gh.validate_credentials.return_value = True
    mock_gh.commit_and_push.return_value = "commit_sha_123"
    
    mock_lc = MagicMock(spec=LeetCodeIntegration)
    mock_lc.validate_session.return_value = True
    # Two submissions, but one is already synced
    mock_lc.get_recent_accepted_submissions.return_value = [
        {"id": "200", "title": "Add Two Numbers", "statusDisplay": "Accepted", "lang": "python3"},
        {"id": "100", "title": "Two Sum", "statusDisplay": "Accepted", "lang": "python3"}
    ]
    mock_lc.get_submission_details.return_value = {
        "code": "print('Two Sum Code')",
        "timestamp": 1609459200,
        "lang": {"name": "python3", "verboseName": "Python3"},
        "question": {
            "questionId": "1",
            "title": "Two Sum",
            "titleSlug": "two-sum",
            "difficulty": "Easy",
            "topicTags": [{"name": "Array", "slug": "array"}]
        }
    }

    # Add submission "200" already to the database to simulate duplicate skip
    existing = SyncedSubmission(
        leetcode_submission_id="200",
        problem_id="2",
        problem_title="Add Two Numbers",
        difficulty="Medium",
        language="python3",
        topic_tags="Linked List",
        solved_at=datetime.utcnow(),
        github_commit_sha="existing_sha",
        github_file_path="some_path",
        synced_at=datetime.utcnow()
    )
    db_session.add(existing)
    db_session.commit()

    service = SyncEngineService(github_client=mock_gh, leetcode_client=mock_lc)
    job = service.run_sync(db_session)
    
    assert job.status == "COMPLETED"
    
    # Verify that only submission "100" (Two Sum) was synced
    db_submissions = db_session.query(SyncedSubmission).all()
    assert len(db_submissions) == 2  # existing "200" + new "100"
    
    new_synced = db_session.query(SyncedSubmission).filter_by(leetcode_submission_id="100").first()
    assert new_synced is not None
    assert new_synced.problem_title == "Two Sum"
    assert new_synced.github_commit_sha == "commit_sha_123"
    assert new_synced.github_file_path == "leetcode/Easy/Arrays/0001_Two_Sum/solution.py"

def test_sync_engine_run_fails_on_validation_errors(db_session: Session):
    mock_gh = MagicMock(spec=GitHubIntegration)
    mock_gh.validate_credentials.return_value = False
    
    mock_lc = MagicMock(spec=LeetCodeIntegration)
    mock_lc.validate_session.return_value = True

    service = SyncEngineService(github_client=mock_gh, leetcode_client=mock_lc)
    job = service.run_sync(db_session)
    
    assert job.status == "FAILED"
    assert "GitHub credentials validation failed" in job.error_message
    
    # Verify error log created
    error_log = db_session.query(SyncLog).filter_by(level="ERROR").first()
    assert error_log is not None
    assert "GITHUB_API" in error_log.message or "failed" in error_log.message
