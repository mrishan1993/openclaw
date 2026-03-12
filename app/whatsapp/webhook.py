"""WhatsApp webhook handler."""
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any

from app.config import get_settings
from app.agent.agent import agent
from app.whatsapp.client import whatsapp_client
from app.conversation.fallback_handler import handle_fallback
from app.services.conversation_service import (
    get_conversation_context, 
    update_conversation_context,
    add_message_to_history,
    clear_conversation_context
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook with WhatsApp Cloud API."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.verify_token:
        logger.info("Webhook verified successfully")
        return int(challenge)

    logger.warning("Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming WhatsApp messages."""
    try:
        body = await request.json()

        entry = body.get("entry", [])
        if not entry:
            return {"status": "ok"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ok"}

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "ok"}

        for message in messages:
            try:
                await process_message(message)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


async def process_message(message: Dict[str, Any]):
    """Process a single WhatsApp message."""
    from_number = message.get("from", "")
    message_text = message.get("text", {}).get("body", "")

    if not from_number or not message_text:
        logger.warning("Missing message details")
        return

    logger.info(f"Message received from {from_number}: {message_text}")

    normalized_from = from_number.lstrip("+")
    normalized_auth = settings.authorized_user.lstrip("+")

    if normalized_from != normalized_auth:
        logger.warning(f"Unauthorized user: {from_number}")
        return

    logger.info(f"Processing authorized message: {message_text}")

    context = get_conversation_context(from_number)
    add_message_to_history(from_number, "user", message_text)

    fallback_response = handle_fallback(message_text, context)
    if fallback_response:
        logger.info(f"Fallback response: {fallback_response}")
        whatsapp_client.send_message(from_number, fallback_response)
        add_message_to_history(from_number, "assistant", fallback_response)
        return

    response = agent.process_message(message_text, context=context)

    whatsapp_client.send_message(from_number, response)
    add_message_to_history(from_number, "assistant", response)
