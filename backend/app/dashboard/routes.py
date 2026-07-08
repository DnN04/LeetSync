import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.config.settings import settings, Settings
from app.infrastructure.database import get_db
from app.models.models import SyncedSubmission, SyncJob, SyncLog
from app.models.schemas import SyncedSubmissionResponse, SyncJobResponse, SyncLogResponse
from app.services.scheduler_service import scheduler_service
from app.services.stats_engine import StatisticsEngineService
from app.integrations.github import GitHubIntegration
from app.integrations.leetcode import LeetCodeIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    """Retrieves current connectivity status, last sync, and scheduler status."""
    gh = GitHubIntegration()
    lc = LeetCodeIntegration()
    
    # Check credentials
    github_auth = gh.validate_credentials()
    leetcode_auth = lc.validate_session()
    
    # Get last job status
    last_job = db.query(SyncJob).order_by(SyncJob.start_time.desc()).first()
    last_job_data = None
    if last_job:
        last_job_data = {
            "id": last_job.id,
            "start_time": last_job.start_time,
            "end_time": last_job.end_time,
            "status": last_job.status,
            "error_message": last_job.error_message
        }
        
    scheduler_status = scheduler_service.get_status()
    
    return {
        "github_connected": github_auth,
        "leetcode_connected": leetcode_auth,
        "github_repo": settings.github_repo,
        "scheduler": scheduler_status,
        "last_sync_job": last_job_data,
        "timestamp": datetime.utcnow()
    }

@router.post("/sync/trigger")
def trigger_manual_sync(background_tasks: BackgroundTasks):
    """Triggers a manual synchronization job in the background."""
    try:
        scheduler_service.trigger_now()
        return {"status": "success", "message": "Manual synchronization queued in the background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue manual sync: {str(e)}")

@router.get("/submissions", response_model=List[SyncedSubmissionResponse])
def get_synced_submissions(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieves the list of synchronized submissions from database."""
    submissions = db.query(SyncedSubmission).order_by(SyncedSubmission.synced_at.desc()).limit(limit).all()
    return submissions

@router.get("/logs", response_model=List[SyncLogResponse])
def get_sync_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieves sync operation logs and errors from database."""
    logs = db.query(SyncLog).order_by(SyncLog.timestamp.desc()).limit(limit).all()
    return logs

@router.get("/statistics")
def get_metrics_and_statistics(db: Session = Depends(get_db)):
    """Compiles total counts, difficulty breakdowns, and topic stats from synced solutions."""
    stats_engine = StatisticsEngineService()
    stats_dict, _ = stats_engine.generate_statistics(db)
    return stats_dict

@router.get("/settings")
def get_current_settings():
    """Fetches the current settings (excluding secret tokens for safety)."""
    return {
        "github_repo": settings.github_repo,
        "sync_interval_minutes": settings.sync_interval_minutes,
        "log_level": settings.log_level,
        "sync_repo_path": settings.sync_repo_path,
        "database_url": settings.database_url,
        "github_token_configured": bool(settings.github_token),
        "leetcode_session_configured": bool(settings.leetcode_session),
        "leetcode_csrf_configured": bool(settings.leetcode_csrf_token)
    }

@router.post("/settings")
def update_settings(payload: Dict[str, Any]):
    """Dynamically updates app setting variables (updates global settings object)."""
    try:
        # Dynamically map changes to local settings object
        if "github_repo" in payload:
            settings.github_repo = payload["github_repo"]
        if "sync_interval_minutes" in payload:
            settings.sync_interval_minutes = int(payload["sync_interval_minutes"])
            # Restart scheduler if running to load new interval
            if scheduler_service.scheduler.running:
                scheduler_service.shutdown()
                scheduler_service.start()
        if "log_level" in payload:
            settings.log_level = payload["log_level"]
            logging.getLogger().setLevel(payload["log_level"])
            
        return {"status": "success", "message": "Settings updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update settings: {str(e)}")
