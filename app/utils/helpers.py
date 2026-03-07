"""Helper utilities."""
from datetime import datetime
from typing import Optional


def parse_datetime(time_str: str) -> Optional[datetime]:
    """Parse datetime from various formats."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%H:%M:%S",
        "%H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue

    return None


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()


def sanitize_phone_number(phone: str) -> str:
    """Sanitize phone number for WhatsApp API."""
    return "".join(c for c in phone if c.isdigit() or c == "+")
