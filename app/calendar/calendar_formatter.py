"""Calendar response formatter."""
from typing import List, Dict, Any
from datetime import datetime


def format_events_list(events: List[Dict[str, Any]]) -> str:
    """Format events list for user response."""
    if not events:
        return "No events found."

    response = "Your events:\n"
    for event in events:
        start = event.get("start", {})
        summary = event.get("summary", "Untitled")

        if "dateTime" in start:
            dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            time_str = dt.strftime("%I:%M %p")
            date_str = dt.strftime("%b %d")
            response += f"• {date_str} at {time_str} - {summary}\n"
        elif "date" in start:
            date_str = start["date"]
            response += f"• {date_str} (All day) - {summary}\n"

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
        emails = [a.get("email", "") for a in attendees[:3]]
        response += f"Attendees: {', '.join(emails)}\n"

    return response.strip()


def format_availability(busy_slots: List[Dict]) -> str:
    """Format availability for user response."""
    if not busy_slots:
        return "You are free!"

    response = "You are busy at:\n"
    for slot in busy_slots[:5]:
        start = slot.get("start", {})
        end = slot.get("end", {})

        if "dateTime" in start:
            start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
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
        response += f"• {start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}\n"

    return response.strip()
