"""Scheduler configuration."""
from apscheduler.schedulers.background import BackgroundScheduler

from app.scheduler.digest import setup_scheduler
from app.utils.logger import get_logger

logger = get_logger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """Start the background scheduler."""
    setup_scheduler(scheduler)
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
