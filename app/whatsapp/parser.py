"""WhatsApp message parser."""
import re
from typing import Optional, Tuple
from datetime import datetime


class MessageParser:
    """Parser for WhatsApp messages."""

    TASK_PATTERNS = [
        r"add (.+) to my tasks?",
        r"remind me to (.+) at (.+)",
        r"new task: (.+)",
        r"task: (.+)",
    ]

    NOTE_PATTERNS = [
        r"note: (.+)",
        r"save this idea: (.+)",
        r"save note: (.+)",
        r"idea: (.+)",
    ]

    SEARCH_PATTERNS = [
        r"what ideas do i have about (.+)\??",
        r"search my notes for (.+)",
        r"find notes about (.+)",
    ]

    TODAY_TASKS_PATTERNS = [
        r"what are my tasks today\??",
        r"show my tasks today",
        r"today's tasks",
    ]

    @classmethod
    def parse_message(cls, message: str) -> Tuple[str, dict]:
        """Parse message and determine intent."""

        message = message.strip()

        for pattern in cls.TASK_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if "remind" in pattern:
                    return "task_with_reminder", {
                        "title": match.group(1).strip(),
                        "due_time": match.group(2).strip(),
                    }
                return "add_task", {"title": match.group(1).strip()}

        for pattern in cls.NOTE_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                tags = cls._extract_tags(content)
                return "save_note", {"content": content, "tags": tags}

        for pattern in cls.SEARCH_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return "search_notes", {"query": match.group(1).strip()}

        for pattern in cls.TODAY_TASKS_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return "get_today_tasks", {}

        return "general", {"message": message}

    @classmethod
    def _extract_tags(cls, content: str) -> Optional[str]:
        """Extract tags from note content."""
        tag_match = re.search(r"\[([^\]]+)\]", content)
        if tag_match:
            return tag_match.group(1)
        return None
