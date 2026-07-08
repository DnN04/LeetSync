import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database import init_db
from app.services.scheduler_service import scheduler_service
from app.dashboard.routes import router as dashboard_router
from app.utilities.logger import setup_logging
from app.config.settings import settings

# Setup JSON logging formatting on startup
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    logger.info("Initializing database schema...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        
    logger.info("Starting background execution scheduler...")
    try:
        scheduler_service.start()
    except Exception as e:
        logger.error(f"Failed to start scheduler on boot: {e}")
        
    yield
    
    # Shutdown Events
    logger.info("Shutting down background scheduler...")
    try:
        scheduler_service.shutdown()
    except Exception as e:
        logger.error(f"Failed to stop scheduler on shutdown: {e}")

app = FastAPI(
    title="LeetSync Pro API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware to support Vite frontend dashboard requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow dashboard access from local browser clients
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include APIs
app.include_router(dashboard_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
