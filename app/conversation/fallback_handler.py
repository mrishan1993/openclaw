"""Conversational fallback handler."""
import re
from typing import Optional

from app.conversation.keyword_sets import (
    POSITIVE_KEYWORDS,
    NEUTRAL_KEYWORDS,
    NEGATIVE_KEYWORDS,
)
from app.conversation.response_bank import get_response
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_FALLBACK_WORDS = 5


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    return text.lower().strip()


def handle_fallback(message: str) -> Optional[str]:
    """Handle conversational fallback messages."""
    if not message:
        return None

    normalized = normalize_text(message)

    ignore_patterns = [
        "what are my tasks",
        "show all tasks",
        "delete task",
        "complete task",
        "show all notes",
        "what ideas do i have",
        "search my notes",
        "add ", "note:", "save this",
    ]

    for pattern in ignore_patterns:
        if pattern in normalized:
            return None

    words = normalized.split()

    if len(words) > MAX_FALLBACK_WORDS:
        return None

    category = detect_category(normalized)

    if category:
        logger.info(f"[FALLBACK] category={category} message={message}")
        return get_response(category)

    return None


def detect_category(text: str) -> Optional[str]:
    """Detect the sentiment category of the message."""
    words = set(text.split())

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
