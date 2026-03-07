"""Main FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.db import init_db
from app.scheduler.scheduler import start_scheduler, stop_scheduler
from app.whatsapp.webhook import router as webhook_router
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting application...")
    init_db()
    logger.info("Database initialized")
    start_scheduler()
    logger.info("Scheduler started")
    yield
    logger.info("Shutting down...")
    stop_scheduler()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="WhatsApp Personal Assistant",
    description="AI-powered WhatsApp assistant for managing tasks and notes",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(webhook_router, prefix="", tags=["whatsapp"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "ok", "message": "WhatsApp Personal Assistant is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
