"""Calendar tools for the AI agent."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.calendar.calendar_mcp_client import CalendarClient
from app.calendar.calendar_formatter import (
    format_events_list,
    format_event_details,
    format_availability,
    format_free_slots,
    format_daily_agenda,
)
from app.calendar.calendar_utils import is_valid_email, extract_primary_meeting_link
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
        time_min = datetime.combine(now.date(), datetime.min.time()).isoformat() + "+05:30"
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
        time_min = datetime.combine(tomorrow.date(), datetime.min.time()).isoformat() + "+05:30"
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


def delete_event(
    query: Optional[str] = None, 
    event_id: Optional[str] = None, 
    phone_number: Optional[str] = None
) -> Dict[str, Any]:
    """Delete an event by ID or by searching for a match."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        
        # If event_id is provided, delete it directly
        if event_id:
            logger.info(f"[CALENDAR] delete_event - event_id: {event_id}")
            del_result = client.delete_event(event_id)
            if del_result.get("success"):
                return {"success": True, "message": "Successfully cancelled the meeting."}
            return del_result

        # Otherwise, use query to search
        if not query:
            return {"success": False, "message": "Please provide either an event ID or a search query to cancel."}

        logger.info(f"[CALENDAR] delete_event - query: {query}")
        
        # 1. Parse query for potential date/time and title
        # Handle formatted strings like "Mar 14, 2026 at 02:30 PM - Meeting Title"
        query_parts = query.split(" - ", 1)
        search_query = query
        has_formatted_prefix = False
        
        if len(query_parts) == 2:
            search_query = query_parts[1]
            has_formatted_prefix = True
            logger.info(f"[CALENDAR] Detected formatted string pattern. Using title: {search_query}")

        # 2. Setup search window
        # If the query contains a date hint, we should search around that date
        from app.calendar.calendar_parser import CalendarParser
        parsed_dt = CalendarParser.parse_datetime(query)
        
        if parsed_dt:
            # If we found a specific time, search specifically for that day
            start_dt = datetime.fromisoformat(parsed_dt["start"])
            time_min = datetime.combine(start_dt.date(), datetime.min.time()).isoformat() + "+05:30"
            time_max = datetime.combine(start_dt.date(), datetime.max.time()).isoformat() + "+05:30"
            logger.info(f"[CALENDAR] Found date in query: {start_dt.date()}. Searching that day.")
        else:
            # Default: Search from start of today
            start_of_today = datetime.combine(now.date(), datetime.min.time())
            time_min = start_of_today.isoformat() + "+05:30"
            time_max = None # Upcoming events

        # 3. Search events
        # Use the stripped title if we detected a formatted string
        result = client.list_events(max_results=50, time_min=time_min, time_max=time_max)
        
        if not result.get("success"):
            logger.error(f"[CALENDAR] Failed to list events: {result}")
            return result
        
        all_events = result.get("events", [])
        logger.info(f"[CALENDAR] Found {len(all_events)} candidate events")
        
        if not all_events:
            return {"success": False, "message": f"Could not find any events matching your request to cancel."}
            
        # 4. Refine matching with context (Title, Time, Attendees)
        query_lower = search_query.lower()
        # Break query into words and drop very short/common filler words so we can
        # focus matching on meaningful tokens like names and topics.
        raw_words = [w for w in query_lower.replace(",", " ").split() if w]
        stop_words = {
            "meeting",
            "call",
            "sync",
            "review",
            "my",
            "the",
            "with",
            "on",
            "at",
            "for",
            "next",
            "this",
            "upcoming",
            "today",
            "tomorrow",
        }
        query_words = [w for w in raw_words if len(w) > 2 and w not in stop_words]
        
        matching_events = []
        for event in all_events:
            summary = event.get("summary", "").lower()
            description = event.get("description", "").lower()
            location = event.get("location", "").lower()
            
            # Score match
            is_match = False
            time_match = False
            title_score = 0 # 0 to 1
            
            # Match 1: Time match (if parsed_dt is present)
            if parsed_dt:
                event_start_str = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
                if event_start_str:
                    try:
                        event_start_dt = datetime.fromisoformat(event_start_str.replace("Z", "+00:00"))
                        query_start_dt = datetime.fromisoformat(parsed_dt["start"])
                        
                        # Add UTC offset if query is naive
                        if query_start_dt.tzinfo is None:
                            # Use +05:30 as default (IST)
                            from datetime import timezone, timedelta
                            ist = timezone(timedelta(hours=5, minutes=30))
                            query_start_dt = query_start_dt.replace(tzinfo=ist)
                            
                        # If time matches within 10 minutes
                        if abs((event_start_dt - query_start_dt).total_seconds()) < 600:
                             time_match = True
                    except Exception as te:
                        logger.error(f"[CALENDAR] Time comparison error: {te}")

            # Match 2: Title and keyword matches
            summary_lower = summary.lower()
            if query_lower in summary_lower:
                title_score = 1.0
            elif query_words:
                matched_words = [w for w in query_words if w in summary_lower]
                title_score = len(matched_words) / len(query_words)
            
            # Final decision logic:
            # 1. Exact title match is always a match
            if title_score == 1.0:
                is_match = True
            # 2. Exact time match AND some title overlap (even if just one word)
            elif time_match and (title_score > 0 or not query_words):
                is_match = True
            # 3. High title overlap (more than 50% of words)
            elif title_score > 0.5:
                is_match = True
            # 4. If query was just a date/time (no real title words) and time matches
            elif time_match and not query_words:
                is_match = True
            # 5. Attendee name/email match: if any meaningful query word appears
            #    in an attendee email or display name, treat it as a match.
            elif not is_match:
                attendees = event.get("attendees", [])
                for attendee in attendees:
                    email = attendee.get("email", "").lower()
                    display_name = attendee.get("displayName", "").lower()
                    # Direct full-query match (backwards compatible)
                    if query_lower and (query_lower in email or query_lower in display_name):
                        is_match = True
                        break
                    # Any key word like a person's name inside the attendee fields
                    if any(w in email or w in display_name for w in query_words):
                        is_match = True
                        break
            
            if is_match:
                matching_events.append(event)
        
        logger.info(f"[CALENDAR] Found {len(matching_events)} refined matching events")
        
        if not matching_events:
            return {"success": False, "message": f"Could not find a specific match for '{query}'. Please check the name or time and try again."}
            
        if len(matching_events) == 1:
            event = matching_events[0]
            event_id = event["id"]
            summary = event.get("summary", "Untitled")
            
            # Safety: Check if this event started more than 7 days ago
            start_str = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
            if start_str:
                try:
                    start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    if start_dt < (now - timedelta(days=7)):
                        return {"success": False, "message": f"The event '{summary}' is too far in the past to cancel."}
                except:
                    pass

            logger.info(f"[CALENDAR] Deleting event: {summary} (id: {event_id})")
            del_result = client.delete_event(event_id)
            if del_result.get("success"):
                return {"success": True, "message": f"Successfully cancelled: {summary}"}
            return del_result
        
        # Multiple matches - show user with details
        return {
            "success": False,
            "message": f"Found {len(matching_events)} events that match your request. Which one would you like to cancel?\n\n" + format_events_list(matching_events)
        }
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
        
        # Search future events only
        now = datetime.now()
        time_min = now.isoformat() + "+05:30"
        
        result = client.list_events(max_results=50, time_min=time_min)
        
        if result.get("success"):
            all_events = result.get("events", [])
            
            # Filter events that match the query
            query_lower = query.lower()
            matching_events = []
            
            for event in all_events:
                summary = event.get("summary", "").lower()
                description = event.get("description", "").lower()
                location = event.get("location", "").lower()
                
                # Check if query matches any part of the event
                if query_lower in summary or query_lower in description or query_lower in location:
                    matching_events.append(event)
                # Also check if key parts match
                elif any(word in summary for word in query_lower.split() if len(word) > 2):
                    matching_events.append(event)
            
            logger.info(f"[CALENDAR] search_events found {len(matching_events)} matching events")
            return {
                "success": True,
                "message": format_events_list(matching_events),
                "events": matching_events,
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


def find_free_slots(time_min_str: str, time_max_str: str, duration_minutes: int = 30, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Find available time slots."""
    try:
        client = _get_calendar_client(phone_number)
        
        # Parse inputs expecting ISO formatted strings
        time_min_dt = datetime.fromisoformat(time_min_str.replace("Z", "+00:00"))
        time_max_dt = datetime.fromisoformat(time_max_str.replace("Z", "+00:00"))
        
        from datetime import timezone
        ist = timezone(timedelta(hours=5, minutes=30))
        
        if time_min_dt.tzinfo is None:
            time_min_dt = time_min_dt.replace(tzinfo=ist)
        if time_max_dt.tzinfo is None:
            time_max_dt = time_max_dt.replace(tzinfo=ist)
            
        time_min = time_min_dt.isoformat()
        time_max = time_max_dt.isoformat()

        result = client.check_free_busy(time_min, time_max)
        
        if not result.get("success"):
            return {"success": False, "message": "Could not check availability"}

        data = result.get("data", {})
        calendars = data.get("calendars", {})
        primary = calendars.get("primary", {})
        busy = primary.get("busy", [])

        free_slots = []
        
        current_time = time_min_dt
        end_of_search = time_max_dt

        busy_sorted = sorted(busy, key=lambda x: x.get("start", "") if isinstance(x.get("start"), str) else x.get("start", {}).get("dateTime", ""))
        
        for slot in busy_sorted:
            start_val = slot.get("start", "")
            if isinstance(start_val, dict):
                start_val = start_val.get("dateTime", start_val.get("date", ""))
                
            end_val = slot.get("end", "")
            if isinstance(end_val, dict):
                end_val = end_val.get("dateTime", end_val.get("date", ""))
                
            slot_start = datetime.fromisoformat(start_val.replace("Z", "+00:00"))
            slot_end = datetime.fromisoformat(end_val.replace("Z", "+00:00"))
            
            if slot_start.tzinfo is None:
                slot_start = slot_start.replace(tzinfo=ist)
            if slot_end.tzinfo is None:
                slot_end = slot_end.replace(tzinfo=ist)
            
            while current_time + timedelta(minutes=duration_minutes) <= slot_start:
                free_slots.append({
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(minutes=duration_minutes)).isoformat()
                })
                current_time += timedelta(minutes=duration_minutes)
            
            current_time = max(current_time, slot_end)

        while current_time + timedelta(minutes=duration_minutes) <= end_of_search:
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
    """Add attendee to event with validation and duplicate checks."""
    try:
        if not is_valid_email(email):
            logger.info(f"[CALENDAR_ATTENDEE] invalid_email - {email}")
            return {"success": False, "message": "That email address does not appear to be valid."}

        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_ATTENDEE] add_attendee - event_id: {event_id}, email: {email}")

        event_result = client.get_event(event_id)
        if not event_result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = event_result.get("event", {})
        attendees = event.get("attendees", [])
        if any(a.get("email") == email for a in attendees):
            return {"success": False, "message": f"{email} is already invited to this meeting."}

        attendees.append({"email": email})
        update_result = client.update_event(event_id, {"attendees": attendees})
        logger.info(f"[CALENDAR_ATTENDEE] add_attendee result: {update_result.get('success')}")

        if update_result.get("success"):
            return {"success": True, "message": f"{email} has been added to the meeting."}
        return {"success": False, "message": update_result.get("message", "Failed to add attendee")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_ATTENDEE] add_attendee error: {str(e)}")
        return {"success": False, "message": f"Failed to add attendee: {str(e)}"}


def remove_event_attendee(event_id: str, email: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Remove attendee from event with existence checks."""
    try:
        if not is_valid_email(email):
            logger.info(f"[CALENDAR_ATTENDEE] invalid_email - {email}")
            return {"success": False, "message": "That email address does not appear to be valid."}

        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_ATTENDEE] remove_attendee - event_id: {event_id}, email: {email}")

        event_result = client.get_event(event_id)
        if not event_result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = event_result.get("event", {})
        attendees = event.get("attendees", [])
        existing = [a for a in attendees if a.get("email") == email]
        if not existing:
            return {"success": False, "message": f"{email} is not currently listed as an attendee."}

        new_attendees = [a for a in attendees if a.get("email") != email]
        update_result = client.update_event(event_id, {"attendees": new_attendees})
        logger.info(f"[CALENDAR_ATTENDEE] remove_attendee result: {update_result.get('success')}")

        if update_result.get("success"):
            return {"success": True, "message": f"{email} has been removed from the meeting."}
        return {"success": False, "message": update_result.get("message", "Failed to remove attendee")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_ATTENDEE] remove_attendee error: {str(e)}")
        return {"success": False, "message": f"Failed to remove attendee: {str(e)}"}


def list_event_attendees(event_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """List attendees for an event."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_ATTENDEE] list_attendees - event_id: {event_id}")

        result = client.get_event(event_id)
        if not result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = result.get("event", {})
        attendees = event.get("attendees", [])
        if not attendees:
            return {"success": True, "message": "No attendees are currently invited to this meeting.", "attendees": []}

        emails = [a.get("email") for a in attendees if a.get("email")]
        pretty = ", ".join(emails) if emails else "No attendees with email addresses."
        return {"success": True, "message": pretty, "attendees": attendees}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_ATTENDEE] list_attendees error: {str(e)}")
        return {"success": False, "message": f"Failed to list attendees: {str(e)}"}


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
        logger.info(f"[CALENDAR_RECURRING] create_recurring_event - title: {title}, rule: {recurrence_rule}")
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
        logger.error(f"[CALENDAR_RECURRING] create_recurring_event error: {str(e)}")
        return {"success": False, "message": f"Failed to create recurring event: {str(e)}"}


def cancel_recurring_instance(event_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Cancel a single instance of a recurring event (using its instance event ID)."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_RECURRING] cancel_instance - event_id: {event_id}")
        result = client.delete_event(event_id)
        if result.get("success"):
            return {"success": True, "message": "The selected occurrence has been cancelled. The rest of the series remains unchanged."}
        return {"success": False, "message": result.get("message", "Failed to cancel this occurrence.")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_RECURRING] cancel_instance error: {str(e)}")
        return {"success": False, "message": f"Failed to cancel occurrence: {str(e)}"}


def cancel_recurring_series(event_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Cancel an entire recurring series given any instance or the master event id."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_RECURRING] cancel_series - event_id: {event_id}")

        ev_result = client.get_event(event_id)
        if not ev_result.get("success"):
            return {"success": False, "message": "Could not find that recurring meeting."}

        ev = ev_result.get("event", {})
        master_id = ev.get("recurringEventId") or ev.get("id")
        result = client.delete_event(master_id)
        if result.get("success"):
            return {"success": True, "message": "The entire recurring meeting series has been cancelled."}
        return {"success": False, "message": result.get("message", "Failed to cancel the series.")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_RECURRING] cancel_series error: {str(e)}")
        return {"success": False, "message": f"Failed to cancel series: {str(e)}"}


def get_meeting_link(event_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Get primary meeting link for an event."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_MEETING] get_meeting_link - event_id: {event_id}")
        result = client.get_event(event_id)
        if not result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = result.get("event", {})
        primary, all_links = extract_primary_meeting_link(event)
        if not all_links:
            return {"success": True, "message": "This meeting currently does not have a video link.", "links": []}
        if len(all_links) > 1:
            return {
                "success": True,
                "message": f"This meeting has multiple links. The primary one is:\n{primary}",
                "links": all_links,
                "primary": primary,
            }
        return {"success": True, "message": primary, "links": all_links, "primary": primary}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_MEETING] get_meeting_link error: {str(e)}")
        return {"success": False, "message": f"Failed to get meeting link: {str(e)}"}


def add_meeting_link(
    event_id: str,
    platform: str = "google_meet",
    url: Optional[str] = None,
    phone_number: Optional[str] = None,
) -> Dict[str, Any]:
    """Attach a meeting link to an event."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_MEETING] add_meeting_link - event_id: {event_id}, platform: {platform}, url: {url}")

        # If platform is Google Meet, prefer conferenceData
        if platform.lower() in {"google_meet", "meet", "google meet"}:
            from app.calendar.calendar_utils import build_conference_data_for_meet

            conference_data = build_conference_data_for_meet()
            result = client.patch_event_with_conference_data(event_id, conference_data)
            if result.get("success"):
                ev = result.get("event", {})
                primary, _ = extract_primary_meeting_link(ev)
                return {
                    "success": True,
                    "message": f"Google Meet link added: {primary}" if primary else "Google Meet link added.",
                    "event": ev,
                }
            return {"success": False, "message": result.get("message", "Failed to add Google Meet link.")}

        # For Zoom/Teams/custom URLs, fall back to updating description with the link
        if not url:
            return {"success": False, "message": "Please provide a meeting URL to attach."}

        if not url.startswith("http://") and not url.startswith("https://"):
            return {"success": False, "message": "The provided meeting link appears to be invalid."}

        ev_result = client.get_event(event_id)
        if not ev_result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = ev_result.get("event", {})
        description = event.get("description") or ""
        if url in description:
            return {"success": True, "message": "This meeting link is already attached to the event.", "event": event}

        new_description = (description + "\n" if description else "") + f"Meeting link: {url}"
        update_result = client.update_event(event_id, {"description": new_description})
        if update_result.get("success"):
            return {"success": True, "message": "Meeting link added to the event.", "event": update_result.get("event")}
        return {"success": False, "message": update_result.get("message", "Failed to add meeting link.")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_MEETING] add_meeting_link error: {str(e)}")
        return {"success": False, "message": f"Failed to add meeting link: {str(e)}"}


def add_reminder(
    event_id: str,
    minutes_before: int,
    method: str = "popup",
    phone_number: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a reminder to an event."""
    try:
        if minutes_before <= 0:
            return {"success": False, "message": "Reminder time must be before the event start time."}

        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_REMINDER] add_reminder - event_id: {event_id}, minutes_before: {minutes_before}, method: {method}")

        ev_result = client.get_event(event_id)
        if not ev_result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = ev_result.get("event", {})
        reminders = event.get("reminders", {})
        overrides = reminders.get("overrides", []) or []

        overrides.append({"method": method, "minutes": minutes_before})
        result = client.update_event_reminders(event_id, overrides=overrides, use_default=False)
        if result.get("success"):
            return {"success": True, "message": f"Reminder added for {minutes_before} minutes before the meeting."}
        return {"success": False, "message": result.get("message", "Failed to add reminder.")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_REMINDER] add_reminder error: {str(e)}")
        return {"success": False, "message": f"Failed to add reminder: {str(e)}"}


def update_reminder(
    event_id: str,
    index: int,
    minutes_before: int,
    method: Optional[str] = None,
    phone_number: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing reminder by index (0‑based)."""
    try:
        if minutes_before <= 0:
            return {"success": False, "message": "Reminder time must be before the event start time."}

        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_REMINDER] update_reminder - event_id: {event_id}, index: {index}, minutes_before: {minutes_before}, method: {method}")

        ev_result = client.get_event(event_id)
        if not ev_result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = ev_result.get("event", {})
        reminders = event.get("reminders", {})
        overrides = reminders.get("overrides", []) or []

        if not overrides:
            return {"success": False, "message": "This event currently has no reminder set."}
        if index < 0 or index >= len(overrides):
            return {
                "success": False,
                "message": f"This meeting already has {len(overrides)} reminders. Please specify which one to modify (0 to {len(overrides)-1}).",
            }

        overrides[index]["minutes"] = minutes_before
        if method:
            overrides[index]["method"] = method

        result = client.update_event_reminders(event_id, overrides=overrides, use_default=False)
        if result.get("success"):
            return {"success": True, "message": f"Reminder updated to {minutes_before} minutes before the meeting."}
        return {"success": False, "message": result.get("message", "Failed to update reminder.")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_REMINDER] update_reminder error: {str(e)}")
        return {"success": False, "message": f"Failed to update reminder: {str(e)}"}


def remove_reminder(
    event_id: str,
    index: Optional[int] = None,
    phone_number: Optional[str] = None,
) -> Dict[str, Any]:
    """Remove a reminder (by index, or all if index is None)."""
    try:
        client = _get_calendar_client(phone_number)
        logger.info(f"[CALENDAR_REMINDER] remove_reminder - event_id: {event_id}, index: {index}")

        ev_result = client.get_event(event_id)
        if not ev_result.get("success"):
            return {"success": False, "message": "Could not find that event."}

        event = ev_result.get("event", {})
        reminders = event.get("reminders", {})
        overrides = reminders.get("overrides", []) or []

        if not overrides:
            return {"success": False, "message": "This event currently has no reminder set."}

        if index is None:
            # Remove all custom reminders
            result = client.update_event_reminders(event_id, overrides=[], use_default=False)
            if result.get("success"):
                return {"success": True, "message": "All reminders removed from this meeting."}
            return {"success": False, "message": result.get("message", "Failed to remove reminders.")}

        if index < 0 or index >= len(overrides):
            return {
                "success": False,
                "message": f"This meeting already has {len(overrides)} reminders. Which one should I modify (0 to {len(overrides)-1})?",
            }

        overrides.pop(index)
        result = client.update_event_reminders(event_id, overrides=overrides, use_default=False)
        if result.get("success"):
            return {"success": True, "message": "Reminder removed from this meeting."}
        return {"success": False, "message": result.get("message", "Failed to remove reminder.")}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_REMINDER] remove_reminder error: {str(e)}")
        return {"success": False, "message": f"Failed to remove reminder: {str(e)}"}


def get_daily_agenda(phone_number: Optional[str] = None) -> Dict[str, Any]:
    """Return a formatted daily agenda for today."""
    try:
        client = _get_calendar_client(phone_number)
        now = datetime.now()
        time_min = datetime.combine(now.date(), datetime.min.time()).isoformat() + "+05:30"
        time_max = datetime.combine(now.date(), datetime.max.time()).isoformat() + "+05:30"

        logger.info(f"[CALENDAR_AGENDA] get_daily_agenda - time_min: {time_min}, time_max: {time_max}")
        result = client.list_events(max_results=50, time_min=time_min, time_max=time_max)
        if not result.get("success"):
            return {"success": False, "message": "Failed to fetch today's agenda."}

        events = result.get("events", [])
        message = format_daily_agenda(events)
        return {"success": True, "message": message, "events": events}
    except ValueError:
        return _handle_no_token(phone_number)
    except Exception as e:
        logger.error(f"[CALENDAR_AGENDA] get_daily_agenda error: {str(e)}")
        return {"success": False, "message": f"Failed to get daily agenda: {str(e)}"}


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
            try:
                # Try to parse ISO date string (YYYY-MM-DD or full timestamp)
                target = datetime.fromisoformat(date_str[:10]).date()
            except ValueError:
                # Fallback to tomorrow
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
        time_min = datetime.combine(now.date(), datetime.min.time()).isoformat() + "+05:30"
        
        week_end = now + timedelta(days=7)
        time_max = datetime.combine(week_end.date(), datetime.max.time()).isoformat() + "+05:30"
        
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
