"""Calendar tools for the AI agent."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.calendar.calendar_mcp_client import CalendarClient
from app.calendar.calendar_formatter import format_events_list, format_event_details, format_availability, format_free_slots
from app.utils.logger import get_logger
from app.services import user_service

logger = get_logger(__name__)


def _get_calendar_client(phone_number: Optional[str] = None) -> CalendarClient:
    """Get calendar client with user-specific token."""
    if phone_number:
        token = user_service.get_user_google_token(phone_number)
        if token:
            return CalendarClient(access_token=token)
        logger.warning(f"No Google token found for user: {phone_number}")
    return CalendarClient()


def _handle_no_token(phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Handle case when no token is available."""
    return {
        "success": False,
        "message": "Please connect your Google Calendar first. Reply with 'connect calendar' to authenticate."
    }


def create_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: str = "",
    phone_number: Optional[str] = None
) -> Dict[str, Any]:
    """Create a calendar event."""
    try:
        client = _get_calendar_client(phone_number)
        
        attendee_list = []
        if attendees:
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', attendees)
            attendee_list = emails
        
        logger.info(f"[CALENDAR] create_event - title: {title}, start: {start_time}, attendees: {attendee_list}")
        result = client.create_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendee_list if attendee_list else None,
        )
        logger.info(f"[CALENDAR] create_event result: {result.get('success')}")
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] create_event error: {str(e)}")
        return {"success": False, "message": f"Failed to create event: {str(e)}"}


def create_all_day_event(
    title: str,
    date: str,
    description: str = "",
    phone_number: Optional[str] = None
) -> Dict[str, Any]:
    """Create an all-day event."""
    try:
        client = _get_calendar_client(phone_number)
        
        logger.info(f"[CALENDAR] create_all_day_event RAW - title: {title}, date: '{date}'")
        
        now = datetime.now()
        
        # Check if date string contains a day name
        date_lower = date.lower() if date else ""
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        parsed_date = None
        
        # First check if day name is in the date string
        for day_name, day_num in day_map.items():
            if day_name in date_lower:
                target_date = CalendarParser.next_weekday(day_num)
                parsed_date = target_date.isoformat()
                logger.info(f"[CALENDAR] Parsed day '{day_name}' -> {parsed_date}")
                break
        
        # If no day name found, try parsing as date
        if not parsed_date and date:
            try:
                event_date = datetime.fromisoformat(date[:10])
                if event_date.date() >= now.date():
                    parsed_date = date[:10]
                    logger.info(f"[CALENDAR] Using parsed date: {parsed_date}")
            except:
                pass
        
        # If still no valid date, use today
        if not parsed_date:
            parsed_date = now.date().isoformat()
            logger.info(f"[CALENDAR] Using today's date: {parsed_date}")
        
        logger.info(f"[CALENDAR] Final date: {parsed_date}")
        result = client.create_all_day_event(title=title, date=parsed_date, description=description)
        logger.info(f"[CALENDAR] create_all_day_event result: {result.get('success')}")
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] create_all_day_event error: {str(e)}")
        return {"success": False, "message": f"Failed to create event: {str(e)}"}


def list_today_events(phone_number: Optional[str] = None) -> Dict[str, Any]:
    """List today's events."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        time_min = now.isoformat() + "+05:30"
        time_max = datetime.combine(now.date(), datetime.max.time()).isoformat() + "+05:30"
        result = client.list_events(max_results=20, time_min=time_min, time_max=time_max)
        
        if result.get("success"):
            events = result.get("events", [])
            return {
                "success": True,
                "message": format_events_list(events),
                "events": events,
            }
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to list events: {str(e)}"}


def list_tomorrow_events(phone_number: Optional[str] = None) -> Dict[str, Any]:
    """List tomorrow's events."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        time_min = tomorrow.isoformat() + "+05:30"
        time_max = datetime.combine(tomorrow.date(), datetime.max.time()).isoformat() + "+05:30"
        
        result = client.list_events(max_results=20, time_min=time_min, time_max=time_max)
        
        if result.get("success"):
            events = result.get("events", [])
            return {
                "success": True,
                "message": format_events_list(events),
                "events": events,
            }
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to list events: {str(e)}"}


def list_upcoming_events(max_results: int = 10, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """List upcoming events."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        time_min = now.isoformat() + "+05:30"
        result = client.list_events(max_results=max_results, time_min=time_min)
        
        if result.get("success"):
            events = result.get("events", [])
            return {
                "success": True,
                "message": format_events_list(events),
                "events": events,
            }
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to list events: {str(e)}"}


def get_event_details(event_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Get event details."""
    try:
        client = _get_calendar_client(phone_number)
        result = client.get_event(event_id)
        if result.get("success"):
            event = result.get("event")
            return {
                "success": True,
                "message": format_event_details(event),
                "event": event,
            }
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to get event: {str(e)}"}


def delete_event(event_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Delete an event."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR] delete_event - event_id: {event_id}")
        result = client.delete_event(event_id)
        logger.info(f"[CALENDAR] delete_event result: {result.get('success')}")
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] delete_event error: {str(e)}")
        return {"success": False, "message": f"Failed to delete event: {str(e)}"}


def search_events(query: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Search events."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR] search_events - query: {query}")
        result = client.search_events(query)
        if result.get("success"):
            events = result.get("events", [])
            logger.info(f"[CALENDAR] search_events found {len(events)} events")
            return {
                "success": True,
                "message": format_events_list(events),
                "events": events,
            }
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] search_events error: {str(e)}")
        return {"success": False, "message": f"Failed to search events: {str(e)}"}


def check_availability(date_str: str = "today", phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Check availability."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        
        if date_str == "today":
            time_min = datetime.combine(now.date(), datetime.min.time()).isoformat() + "+05:30"
            time_max = datetime.combine(now.date(), datetime.max.time()).isoformat() + "+05:30"
        else:
            target = now + timedelta(days=1)
            time_min = datetime.combine(target.date(), datetime.min.time()).isoformat() + "+05:30"
            time_max = datetime.combine(target.date(), datetime.max.time()).isoformat() + "+05:30"

        result = client.check_free_busy(time_min, time_max)
        
        if result.get("success"):
            data = result.get("data", {})
            calendars = data.get("calendars", {})
            primary = calendars.get("primary", {})
            busy = primary.get("busy", [])
            return {
                "success": True,
                "message": format_availability(busy),
            }
        return {"success": False, "message": "Could not check availability"}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to check availability: {str(e)}"}


def find_free_slots(date_str: str = "tomorrow", duration_minutes: int = 30, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Find available time slots."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        
        if date_str == "today":
            target = now.date()
        elif date_str == "tomorrow":
            target = (now + timedelta(days=1)).date()
        else:
            target = (now + timedelta(days=1)).date()

        time_min = datetime.combine(target, datetime.min.time()).isoformat() + "+05:30"
        time_max = datetime.combine(target, datetime.max.time()).isoformat() + "+05:30"

        result = client.check_free_busy(time_min, time_max)
        
        if not result.get("success"):
            return {"success": False, "message": "Could not check availability"}

        data = result.get("data", {})
        calendars = data.get("calendars", {})
        primary = calendars.get("primary", {})
        busy = primary.get("busy", [])

        free_slots = []
        current_time = datetime.combine(target, datetime.min.time())
        end_of_day = datetime.combine(target, datetime.max.time().replace(hour=23, minute=59))

        busy_sorted = sorted(busy, key=lambda x: x.get("start", {}).get("dateTime", ""))
        
        for slot in busy_sorted:
            slot_start = datetime.fromisoformat(slot["start"]["dateTime"].replace("Z", "+00:00").replace("+05:30", ""))
            slot_end = datetime.fromisoformat(slot["end"]["dateTime"].replace("Z", "+00:00").replace("+05:30", ""))
            
            while current_time + timedelta(minutes=duration_minutes) <= slot_start:
                free_slots.append({
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(minutes=duration_minutes)).isoformat()
                })
                current_time += timedelta(minutes=duration_minutes)
            
            current_time = max(current_time, slot_end)

        while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
            free_slots.append({
                "start": current_time.isoformat(),
                "end": (current_time + timedelta(minutes=duration_minutes)).isoformat()
            })
            current_time += timedelta(minutes=duration_minutes)

        return {
            "success": True,
            "message": format_free_slots(free_slots),
            "slots": free_slots,
        }
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to find slots: {str(e)}"}


def reschedule_event(event_id: str, new_start: str, new_end: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Reschedule an event to new time."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR] reschedule_event - event_id: {event_id}, new_start: {new_start}")
        result = client.reschedule_event(event_id, new_start, new_end)
        logger.info(f"[CALENDAR] reschedule_event result: {result.get('success')}")
        if result.get("success"):
            return {"success": True, "message": "Event rescheduled."}
        return {"success": False, "message": result.get("message", "Failed to reschedule")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] reschedule_event error: {str(e)}")
        return {"success": False, "message": f"Failed to reschedule: {str(e)}"}


def change_event_title(event_id: str, new_title: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Change event title."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR] change_event_title - event_id: {event_id}, new_title: {new_title}")
        result = client.change_event_title(event_id, new_title)
        logger.info(f"[CALENDAR] change_event_title result: {result.get('success')}")
        if result.get("success"):
            return {"success": True, "message": f"Event renamed to '{new_title}'."}
        return {"success": False, "message": result.get("message", "Failed to rename event")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] change_event_title error: {str(e)}")
        return {"success": False, "message": f"Failed to rename: {str(e)}"}


def add_event_attendee(event_id: str, email: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Add attendee to event."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR] add_event_attendee - event_id: {event_id}, email: {email}")
        result = client.add_attendee_to_event(event_id, email)
        logger.info(f"[CALENDAR] add_event_attendee result: {result.get('success')}")
        if result.get("success"):
            return {"success": True, "message": f"Added {email} to event."}
        return {"success": False, "message": result.get("message", "Failed to add attendee")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] add_event_attendee error: {str(e)}")
        return {"success": False, "message": f"Failed to add attendee: {str(e)}"}


def remove_event_attendee(event_id: str, email: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Remove attendee from event."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR] remove_event_attendee - event_id: {event_id}, email: {email}")
        result = client.remove_attendee_from_event(event_id, email)
        logger.info(f"[CALENDAR] remove_event_attendee result: {result.get('success')}")
        if result.get("success"):
            return {"success": True, "message": f"Removed {email} from event."}
        return {"success": False, "message": result.get("message", "Failed to remove attendee")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR] remove_event_attendee error: {str(e)}")
        return {"success": False, "message": f"Failed to remove attendee: {str(e)}"}


def create_recurring_event(
    title: str,
    start_time: str,
    end_time: str,
    recurrence_rule: str,
    description: str = "",
    location: str = "",
    phone_number: Optional[str] = None
) -> Dict[str, Any]:
    """Create a recurring event."""
    try:
        client = _get_calendar_client(phone_number)
        result = client.create_recurring_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            recurrence_rule=recurrence_rule,
            description=description,
            location=location,
        )
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to create recurring event: {str(e)}"}


def list_events_by_date(date_str: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """List events for a specific date."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        
        if date_str == "today":
            target = now.date()
        elif date_str == "tomorrow":
            target = (now + timedelta(days=1)).date()
        else:
            target = (now + timedelta(days=1)).date()

        time_min = datetime.combine(target, datetime.min.time()).isoformat() + "+05:30"
        time_max = datetime.combine(target, datetime.max.time()).isoformat() + "+05:30"
        
        result = client.list_events(max_results=50, time_min=time_min, time_max=time_max)
        
        if result.get("success"):
            events = result.get("events", [])
            return {
                "success": True,
                "message": format_events_list(events),
                "events": events,
            }
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to list events: {str(e)}"}


def list_week_events(phone_number: Optional[str] = None) -> Dict[str, Any]:
    """List this week's events."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        time_min = now.isoformat() + "+05:30"
        
        result = client.list_events(max_results=50, time_min=time_min)
        
        if result.get("success"):
            events = result.get("events", [])
            return {
                "success": True,
                "message": format_events_list(events),
                "events": events,
            }
        return result
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to list events: {str(e)}"}


def check_specific_time(time_min: str, time_max: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Check if a specific time slot is free."""
    try:
        client = _get_calendar_client(phone_number)
        result = client.check_free_busy(time_min, time_max)
        
        if result.get("success"):
            data = result.get("data", {})
            calendars = data.get("calendars", {})
            primary = calendars.get("primary", {})
            busy = primary.get("busy", [])
            
            if busy:
                return {
                    "success": True,
                    "message": "You are busy during that time.",
                    "busy": True,
                    "busy_slots": busy,
                }
            return {
                "success": True,
                "message": "You are free during that time.",
                "busy": False,
            }
        return {"success": False, "message": "Could not check availability"}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        return {"success": False, "message": f"Failed to check: {str(e)}"}


def has_calendar_access(phone_number: str) -> bool:
    """Check if user has Google Calendar connected."""
    return user_service.has_google_access(phone_number)
