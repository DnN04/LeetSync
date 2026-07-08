import os
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database import Base, get_db
from app.models.models import SyncedSubmission, SyncJob, SyncLog

TEST_DB_FILE = "test_dashboard.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

# Setup Test Database for routes using a file-based sqlite to ensure tables persist
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session", autouse=True)
def fixture_db_session():
    # Remove old test DB file if present
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass
            
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    
    # Cleanup DB file after test completes
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass

@pytest.fixture(name="client")
def fixture_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@patch("app.dashboard.routes.GitHubIntegration.validate_credentials")
@patch("app.dashboard.routes.LeetCodeIntegration.validate_session")
def test_get_status(mock_lc_val, mock_gh_val, client):
    mock_gh_val.return_value = True
    mock_lc_val.return_value = True
    
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["github_connected"] is True
    assert data["leetcode_connected"] is True

def test_get_settings(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "github_repo" in data
    assert "sync_interval_minutes" in data

def test_update_settings(client):
    response = client.post("/api/settings", json={"sync_interval_minutes": 10})
    assert response.status_code == 200
    
    # Verify it updated settings
    from app.config.settings import settings
    assert settings.sync_interval_minutes == 10
