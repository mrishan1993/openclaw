"""Daily digest scheduler."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.services.task_service import task_service
from app.services.note_service import note_service
from app.whatsapp.client import whatsapp_client
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def send_digest():
    """Send daily digest to authorized user."""
    logger.info("Sending daily digest")

    try:
        tasks = task_service.get_today_tasks()
        notes = note_service.get_recent_notes(limit=5)

        whatsapp_client.send_daily_digest(
            to=settings.authorized_user,
            tasks=tasks,
            notes=notes,
        )
        logger.info("Daily digest sent successfully")
    except Exception as e:
        logger.error(f"Failed to send daily digest: {e}")


def setup_scheduler(scheduler: BackgroundScheduler):
    """Setup daily digest scheduler."""
    hour, minute = settings.digest_time.split(":")

    scheduler.add_job(
        send_digest,
        CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_digest",
        name="Send daily digest",
        replace_existing=True,
    )

    logger.info(f"Daily digest scheduled for {settings.digest_time}")
