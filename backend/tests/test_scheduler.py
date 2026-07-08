import pytest
from unittest.mock import patch, MagicMock
from app.services.scheduler_service import SchedulerService, execute_sync_job

def test_scheduler_status_stopped():
    service = SchedulerService()
    status = service.get_status()
    assert status["status"] == "STOPPED"
    assert len(status["active_jobs"]) == 0

def test_scheduler_lifecycle():
    service = SchedulerService()
    try:
        service.start()
        status = service.get_status()
        assert status["status"] == "RUNNING"
        assert len(status["active_jobs"]) == 1
        assert status["active_jobs"][0]["id"] == "leetsync_recurring_sync"
    finally:
        service.shutdown()
        status = service.get_status()
        assert status["status"] == "STOPPED"

@patch("app.services.sync_engine.SyncEngineService.run_sync")
@patch("app.services.scheduler_service.SessionLocal")
def test_execute_sync_job(mock_session_class, mock_run_sync):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    execute_sync_job()
    
    mock_session_class.assert_called_once()
    mock_run_sync.assert_called_once_with(mock_session)
    mock_session.close.assert_called_once()
