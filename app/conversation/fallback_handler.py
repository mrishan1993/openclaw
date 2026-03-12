"""Conversational fallback handler."""
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.conversation_service import ConversationContext

from app.conversation.keyword_sets import (
    POSITIVE_KEYWORDS,
    NEUTRAL_KEYWORDS,
    NEGATIVE_KEYWORDS,
    GREETING_KEYWORDS,
)
from app.conversation.response_bank import get_response
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_FALLBACK_WORDS = 5


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    return text.lower().strip()


def handle_fallback(message: str, context: Optional["ConversationContext"] = None) -> Optional[str]:
    """Handle conversational fallback messages."""
    if not message:
        return None

    normalized = normalize_text(message)
    msg_lower = normalized

    if context and context.last_action:
        if context.last_action == "awaiting_event_title" and msg_lower != "cancel":
            update_conversation_context(context.phone_number, last_action=None)
            from app.calendar import calendar_tools
            from app.calendar.calendar_parser import CalendarParser
            
            date = context.pending_confirmation
            if date:
                result = calendar_tools.create_all_day_event(
                    title=message,
                    date=date
                )
                if result.get("success"):
                    clear_conversation_context(context.phone_number)
                    return f"All-day event created: {message} on {date}"
                return result.get("message", "Failed to create event")
        
        if context.last_action == "awaiting_all_day_event_date":
            if msg_lower in ["yes", "yeah", "confirm"]:
                if context.last_event_details and context.last_event_details.get("title"):
                    from app.calendar import calendar_tools
                    result = calendar_tools.create_all_day_event(
                        title=context.last_event_details["title"],
                        date=context.pending_confirmation
                    )
                    if result.get("success"):
                        clear_conversation_context(context.phone_number)
                        return f"All-day event created: {context.last_event_details['title']}"
                    return result.get("message", "Failed to create event")
            elif msg_lower == "no" or msg_lower == "cancel":
                clear_conversation_context(context.phone_number)
                return "Event cancelled."
            return None

    ignore_patterns = [
        "what are my tasks",
        "show all tasks",
        "delete task",
        "complete task",
        "show all notes",
        "what ideas do i have",
        "search my notes",
        "add ", "note:", "save this",
        "schedule",
        "meeting",
        "calendar",
        "event",
        "tomorrow at",
        "today at",
        "create event",
    ]

    for pattern in ignore_patterns:
        if pattern in msg_lower:
            return None

    words = msg_lower.split()

    if len(words) > MAX_FALLBACK_WORDS:
        return None

    category = detect_category(msg_lower)

    if category:
        logger.info(f"[FALLBACK] category={category} message={message}")
        return get_response(category)

    return None


def update_conversation_context(phone_number: str, **kwargs):
    """Helper to update context from fallback handler."""
    from app.services.conversation_service import update_conversation_context as update_ctx
    update_ctx(phone_number, **kwargs)


def clear_conversation_context(phone_number: str):
    """Helper to clear context from fallback handler."""
    from app.services.conversation_service import clear_conversation_context as clear_ctx
    clear_ctx(phone_number)


def detect_category(text: str) -> Optional[str]:
    """Detect the sentiment category of the message."""
    words = set(text.split())

    for keyword in GREETING_KEYWORDS:
        if keyword in words or keyword == text:
            return "greeting"
        if " " in keyword and keyword in text:
            return "greeting"

    for keyword in POSITIVE_KEYWORDS:
        if keyword in words or keyword == text:
            return "positive"
        if " " in keyword and keyword in text:
            return "positive"

    for keyword in NEGATIVE_KEYWORDS:
        if keyword in words or keyword == text:
            return "negative"
        if " " in keyword and keyword in text:
            return "negative"

    for keyword in NEUTRAL_KEYWORDS:
        if keyword in words or keyword == text:
            return "neutral"

    return None
