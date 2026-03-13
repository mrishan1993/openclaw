"""Shared helpers and validation utilities for calendar features."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.utils.logger import get_logger

logger = get_logger(__name__)


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    """Lightweight email format validation."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def extract_primary_meeting_link(event: Dict[str, Any]) -> Tuple[Optional[str], List[str]]:
    """Extract primary and all meeting links from an event.

    Preference order:
    1. Google Meet: hangoutLink or conferenceData.entryPoints meeting URLs
    2. Any URLs in location
    3. Any URLs in description
    """
    links: List[str] = []

    # 1. Google Meet / conference data
    hangout_link = event.get("hangoutLink")
    if hangout_link:
        links.append(hangout_link)

    conference_data = event.get("conferenceData") or {}
    entry_points = conference_data.get("entryPoints") or []
    for ep in entry_points:
        uri = ep.get("uri")
        if uri and uri not in links:
            links.append(uri)

    # 2. URLs in location / description
    url_pattern = re.compile(r"https?://\S+")
    for field in ("location", "description"):
        val = event.get(field)
        if isinstance(val, str):
            for match in url_pattern.findall(val):
                if match not in links:
                    links.append(match)

    primary = links[0] if links else None
    return primary, links


def build_conference_data_for_meet(request_id: Optional[str] = None) -> Dict[str, Any]:
    """Build conferenceData payload for creating/adding a Google Meet link."""
    # requestId must be unique per request; fall back to timestamp-based if not provided
    if not request_id:
        request_id = f"meet-{int(datetime.now(tz=timezone.utc).timestamp())}"

    return {
        "createRequest": {
            "requestId": request_id,
            "conferenceSolutionKey": {"type": "hangoutsMeet"},
        }
    }


def detect_overlapping_events(events: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """Return list of pairs of overlapping events (best effort, same-day assumption)."""
    # Normalise into (event, start_dt, end_dt)
    normalised: List[Tuple[Dict[str, Any], datetime, datetime]] = []
    for ev in events:
        start = ev.get("start", {})
        end = ev.get("end", {})
        try:
            if "dateTime" in start and "dateTime" in end:
                s = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                e = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
            elif "date" in start and "date" in end:
                # All‑day – treat as full‑day span
                s = datetime.fromisoformat(start["date"])
                e = datetime.fromisoformat(end["date"])
            else:
                continue
        except Exception:
            continue
        normalised.append((ev, s, e))

    overlaps: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for i in range(len(normalised)):
        for j in range(i + 1, len(normalised)):
            ev1, s1, e1 = normalised[i]
            ev2, s2, e2 = normalised[j]
            if s1 < e2 and s2 < e1:
                overlaps.append((ev1, ev2))
    return overlaps


def to_ist(dt: datetime) -> datetime:
    """Convert a datetime to Asia/Kolkata."""
    ist = timezone(timedelta(hours=5, minutes=30))
    if dt.tzinfo:
        return dt.astimezone(ist)
    return dt.replace(tzinfo=ist)

