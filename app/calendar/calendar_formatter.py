"""Calendar response formatter."""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

from app.calendar.calendar_utils import extract_primary_meeting_link, detect_overlapping_events, to_ist


def format_events_list(events: List[Dict[str, Any]]) -> str:
    """Format events list for user response."""
    if not events:
        return "No events found."

    response = ""
    for i, event in enumerate(events, 1):
        start = event.get("start", {})
        summary = event.get("summary", "Untitled")

        if "dateTime" in start:
            dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            if dt.tzinfo:
                ist = timezone(timedelta(hours=5, minutes=30))
                dt = dt.astimezone(ist)
            time_str = dt.strftime("%I:%M %p")
            date_str = dt.strftime("%b %d, %Y")
            response += f"{i}. {date_str} at {time_str} - {summary}\n"
        elif "date" in start:
            try:
                dt = datetime.fromisoformat(start["date"])
                date_str = dt.strftime("%b %d, %Y")
            except ValueError:
                date_str = start["date"]
            response += f"{i}. {date_str} (All day) - {summary}\n"

    return response.strip()


def format_event_details(event: Dict[str, Any]) -> str:
    """Format event details for user response."""
    summary = event.get("summary", "Untitled")
    
    start = event.get("start", {})
    end = event.get("end", {})

    time_str = ""
    if "dateTime" in start:
        start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
        
        from datetime import timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        if start_dt.tzinfo:
            start_dt = start_dt.astimezone(ist)
        if end_dt.tzinfo:
            end_dt = end_dt.astimezone(ist)
            
        time_str = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
    elif "date" in start:
        time_str = "All day event"

    location = event.get("location", "")
    description = event.get("description", "")

    response = f"**{summary}**\n"
    response += f"Time: {time_str}\n"

    if location:
        response += f"Location: {location}\n"

    if description:
        response += f"Description: {description[:100]}\n"

    attendees = event.get("attendees", [])
    if attendees:
        emails = [a.get("email", "") for a in attendees[:3] if a.get("email")]
        if emails:
            response += f"Attendees: {', '.join(emails)}\n"

    primary_link, _ = extract_primary_meeting_link(event)
    if primary_link:
        response += f"Meeting link: {primary_link}\n"

    return response.strip()


def format_availability(busy_slots: List[Dict]) -> str:
    """Format availability for user response."""
    if not busy_slots:
        return "You are free!"

    response = "You are busy at:\n"
    for slot in busy_slots[:5]:
        start = slot.get("start")
        end = slot.get("end")

        if isinstance(start, str):
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        elif isinstance(start, dict) and "dateTime" in start:
            start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
        else:
            continue
            
        from datetime import timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        if start_dt.tzinfo:
            start_dt = start_dt.astimezone(ist)
        if end_dt.tzinfo:
            end_dt = end_dt.astimezone(ist)
            
        response += f"• {start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}\n"

    return response.strip()


def format_free_slots(slots: List[Dict]) -> str:
    """Format free slots for user response."""
    if not slots:
        return "No available slots found."

    response = "Available slots:\n"
    for slot in slots[:5]:
        start = slot.get("start", {})
        end = slot.get("end", {})

        if isinstance(start, str):
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        elif "dateTime" in start:
            start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
        else:
            continue

        start_dt = to_ist(start_dt)
        end_dt = to_ist(end_dt)
            
        response += f"• {start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}\n"

    return response.strip()


def format_daily_agenda(events: List[Dict[str, Any]]) -> str:
    """Format a daily agenda including times, titles, locations, and meeting links."""
    if not events:
        return "You have no scheduled events today."

    # Separate all‑day vs timed
    all_day_events: List[Dict[str, Any]] = []
    timed_events: List[Dict[str, Any]] = []

    for ev in events:
        start = ev.get("start", {})
        if "date" in start and "dateTime" not in start:
            all_day_events.append(ev)
        else:
            timed_events.append(ev)

    # Sort timed events by start time
    def _start_key(ev: Dict[str, Any]) -> datetime:
        start = ev.get("start", {})
        if "dateTime" in start:
            dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
        elif "date" in start:
            dt = datetime.fromisoformat(start["date"])
        else:
            dt = datetime.now()
        return to_ist(dt)

    timed_events.sort(key=_start_key)

    lines: List[str] = []
    lines.append("Your schedule today:\n")

    for ev in timed_events:
        start = ev.get("start", {})
        end = ev.get("end", {})
        summary = ev.get("summary", "Untitled")
        location = ev.get("location", "")
        primary_link, _ = extract_primary_meeting_link(ev)

        start_dt = None
        if "dateTime" in start:
            start_dt = to_ist(datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00")))
        elif "date" in start:
            start_dt = to_ist(datetime.fromisoformat(start["date"]))

        if start_dt:
            time_str = start_dt.strftime("%H:%M")
        else:
            time_str = "Time N/A"

        base = f"{time_str} – {summary}"
        details: List[str] = []
        if location:
            details.append(location)
        if primary_link:
            details.append(primary_link)

        if details:
            base += " (" + ", ".join(details) + ")"

        lines.append(base)

    if all_day_events:
        lines.append("\nAll-day events:")
        for ev in all_day_events:
            summary = ev.get("summary", "Untitled")
            lines.append(summary)

    # Overlap notice
    overlaps = detect_overlapping_events(events)
    if overlaps:
        lines.append("\nNote: You have overlapping events today.")

    return "\n".join(lines).strip()
