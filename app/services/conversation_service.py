"""Conversation context service for storing user conversation history."""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConversationContext:
    """Stores context for a user's conversation."""
    phone_number: str
    last_action: Optional[str] = None
    last_event_details: Optional[Dict[str, Any]] = None
    pending_confirmation: Optional[str] = None
    history: List[Dict[str, str]] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)


class ConversationStore:
    """In-memory store for conversation contexts."""

    def __init__(self):
        self._store: Dict[str, ConversationContext] = {}
        self._cleanup_old()

    def _cleanup_old(self):
        """Remove contexts older than 10 minutes."""
        cutoff = datetime.now() - timedelta(minutes=10)
        for phone, context in list(self._store.items()):
            if context.updated_at < cutoff:
                del self._store[phone]

    def get_context(self, phone_number: str) -> ConversationContext:
        """Get or create context for a phone number."""
        self._cleanup_old()
        if phone_number not in self._store:
            self._store[phone_number] = ConversationContext(phone_number=phone_number)
        return self._store[phone_number]

    def update_context(self, phone_number: str, **kwargs):
        """Update context with new values."""
        context = self.get_context(phone_number)
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
        context.updated_at = datetime.now()

    def add_to_history(self, phone_number: str, role: str, content: str):
        """Add a message to conversation history."""
        context = self.get_context(phone_number)
        context.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        context.updated_at = datetime.now()

    def clear_context(self, phone_number: str):
        """Clear context for a phone number."""
        if phone_number in self._store:
            del self._store[phone_number]

    def get_last_user_message(self, phone_number: str) -> Optional[str]:
        """Get the last user message from history."""
        context = self.get_context(phone_number)
        for msg in reversed(context.history):
            if msg["role"] == "user":
                return msg["content"]
        return None


conversation_store = ConversationStore()


def get_conversation_context(phone_number: str) -> ConversationContext:
    """Get conversation context for a user."""
    return conversation_store.get_context(phone_number)


def update_conversation_context(phone_number: str, **kwargs):
    """Update conversation context."""
    conversation_store.update_context(phone_number, **kwargs)


def add_message_to_history(phone_number: str, role: str, content: str):
    """Add message to conversation history."""
    conversation_store.add_to_history(phone_number, role, content)


def clear_conversation_context(phone_number: str):
    """Clear conversation context."""
    conversation_store.clear_context(phone_number)
