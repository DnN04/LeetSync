from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.infrastructure.database import Base
from app.models.models import SyncedSubmission
from app.services.stats_engine import StatisticsEngineService

@pytest.fixture(name="db_session")
def fixture_db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionClass = sessionmaker(bind=engine)
    session = SessionClass()
    yield session
    session.close()

def test_statistics_aggregation(db_session: Session):
    # Add dummy submissions to database
    sub1 = SyncedSubmission(
        leetcode_submission_id="100",
        problem_id="1",
        problem_title="Two Sum",
        difficulty="Easy",
        language="python3",
        topic_tags="Array,Hash Table",
        solved_at=datetime(2026, 1, 1),
        github_commit_sha="sha1",
        github_file_path="leetcode/Easy/Arrays/0001_Two_Sum/solution.py"
    )
    sub2 = SyncedSubmission(
        leetcode_submission_id="101",
        problem_id="2",
        problem_title="Add Two Numbers",
        difficulty="Medium",
        language="python3",
        topic_tags="Linked List,Recursion",
        solved_at=datetime(2026, 1, 2),
        github_commit_sha="sha2",
        github_file_path="leetcode/Medium/Linked_Lists/0002_Add_Two_Numbers/solution.py"
    )
    sub3 = SyncedSubmission(
        leetcode_submission_id="102",
        problem_id="3",
        problem_title="Reverse Integer",
        difficulty="Easy",
        language="java",
        topic_tags="Math",
        solved_at=datetime(2026, 1, 3),
        github_commit_sha="sha3",
        github_file_path="leetcode/Easy/Math/0003_Reverse_Integer/solution.java"
    )
    db_session.add_all([sub1, sub2, sub3])
    db_session.commit()

    service = StatisticsEngineService()
    stats, readme = service.generate_statistics(db_session)

    # Assert aggregations
    assert stats["total_solved"] == 3
    assert stats["difficulty_breakdown"]["Easy"] == 2
    assert stats["difficulty_breakdown"]["Medium"] == 1
    assert stats["difficulty_breakdown"]["Hard"] == 0
    assert stats["topic_distribution"]["Array"] == 1
    assert stats["topic_distribution"]["Math"] == 1

    # Assert readme output contains tables and activity details
    assert "# LeetCode Portfolio" in readme
    assert "🟢 Easy | 2" in readme
    assert "🟡 Medium | 1" in readme
    assert "Reverse Integer" in readme
    assert "Two Sum" in readme
