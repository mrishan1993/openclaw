"""Reminder scheduler."""
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from app.services.task_service import task_service
from app.whatsapp.client import whatsapp_client
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def send_reminder(task_id: int):
    """Send reminder for a specific task."""
    logger.info(f"Sending reminder for task {task_id}")

    try:
        task = task_service.get_task_by_id(task_id)
        if task and not task["completed"]:
            message = f"Reminder: {task['title']}"
            whatsapp_client.send_message(settings.authorized_user, message)
            logger.info(f"Reminder sent for task {task_id}")
    except Exception as e:
        logger.error(f"Failed to send reminder: {e}")


def schedule_reminder(scheduler: BackgroundScheduler, task_id: int, due_time: datetime):
    """Schedule a reminder for a task."""
    job_id = f"reminder_{task_id}"

    scheduler.add_job(
        send_reminder,
        "date",
        run_date=due_time,
        args=[task_id],
        id=job_id,
        name=f"Reminder for task {task_id}",
        replace_existing=True,
    )

    logger.info(f"Reminder scheduled for task {task_id} at {due_time}")
