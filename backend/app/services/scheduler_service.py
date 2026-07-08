import logging
from datetime import datetime
from typing import Dict, Any, List
from apscheduler.schedulers.background import BackgroundScheduler
from app.config.settings import settings
from app.infrastructure.database import SessionLocal
from app.services.sync_engine import SyncEngineService

logger = logging.getLogger(__name__)

def execute_sync_job() -> None:
    """Wrapper function executed by the background scheduler to run sync engine."""
    logger.info("Scheduler triggered background synchronization task...")
    db = SessionLocal()
    try:
        engine = SyncEngineService()
        engine.run_sync(db)
    except Exception as e:
        logger.error(f"Scheduled sync execution encountered error: {str(e)}")
    finally:
        db.close()

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.job_id = "leetsync_recurring_sync"

    def start(self) -> None:
        """Starts the background scheduler and schedules the recurring synchronization task."""
        if not self.scheduler.running:
            interval = settings.sync_interval_minutes
            logger.info(f"Starting background scheduler. Interval: {interval} minutes.")
            self.scheduler.add_job(
                execute_sync_job,
                "interval",
                minutes=interval,
                id=self.job_id,
                replace_existing=True
            )
            self.scheduler.start()
            logger.info("Scheduler started successfully.")
        else:
            logger.warning("Scheduler is already running.")

    def shutdown(self) -> None:
        """Safely shuts down the background scheduler."""
        if self.scheduler.running:
            logger.info("Shutting down background scheduler...")
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler shutdown successfully.")
        else:
            logger.warning("Scheduler is not running.")

    def trigger_now(self) -> None:
        """Triggers the sync job immediately in the background."""
        logger.info("Manual synchronization triggered immediately.")
        # Add a one-off job to execute right now in background
        self.scheduler.add_job(execute_sync_job, id="manual_sync_one_off")

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state and list of active jobs for the scheduler.
        
        Returns:
            Dict[str, Any]: Status dictionary.
        """
        is_running = self.scheduler.running
        jobs = []
        
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S UTC") if job.next_run_time else None
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": next_run
            })
            
        return {
            "status": "RUNNING" if is_running else "STOPPED",
            "active_jobs": jobs,
            "sync_interval_minutes": settings.sync_interval_minutes
        }

# Global scheduler service instance
scheduler_service = SchedulerService()
