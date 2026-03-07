"""WhatsApp client for sending messages."""
import httpx
from typing import Optional

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

settings = get_settings()


class WhatsAppClient:
    """Client for sending WhatsApp messages via Cloud API."""

    def __init__(self):
        """Initialize the WhatsApp client."""
        self.phone_id = settings.whatsapp_phone_id
        self.token = settings.whatsapp_token
        self.base_url = "https://graph.facebook.com/v18.0"

    def send_message(self, to: str, message: str) -> bool:
        """Send a WhatsApp message."""
        if not to.startswith("+"):
            to = "+" + to

        url = f"{self.base_url}/{self.phone_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, json=payload)
                logger.info(f"WhatsApp response status: {response.status_code}")
                logger.info(f"WhatsApp response body: {response.text}")
                response.raise_for_status()
                logger.info(f"Sent message to {to}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to send message: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_daily_digest(self, to: str, tasks: list, notes: list) -> bool:
        """Send daily digest message."""
        message = "Good morning!\n\n"

        if tasks:
            message += "Today's tasks:\n"
            for task in tasks:
                message += f"• {task['title']}\n"
        else:
            message += "You have no tasks for today.\n"

        message += "\n"

        if notes:
            message += "Recent notes:\n"
            for note in notes[:5]:
                content = note["content"][:50]
                if len(note["content"]) > 50:
                    content += "..."
                message += f"• {content}\n"
        else:
            message += "No recent notes."

        return self.send_message(to, message)


whatsapp_client = WhatsAppClient()
