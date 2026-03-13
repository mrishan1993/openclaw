"""Calendar message parser."""
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.conversation_service import ConversationContext


class CalendarParser:
    """Parser for calendar-related messages."""

    @staticmethod
    def parse_create_event(message: str, context: Optional["ConversationContext"] = None) -> Optional[Dict[str, Any]]:
        """Parse event creation message."""
        msg = message.lower()
        
        from app.utils.logger import get_logger
        logger = get_logger(__name__)

        if "all day event" in msg or "all-day event" in msg:
            title = None
            date_str = None
            
            title_patterns = [
                r"(?:called|named|title|call) (.+?)(?: for | on | this | tomorrow | monday | tuesday | wednesday | thursday | friday | saturday | sunday |$)",
                r"event (?:called|named|call)? (.+?)(?: for | on | this | tomorrow |$)?",
                r"(.+?) (?:for|on|this) (?:day )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow)",
            ]
            
            for pattern in title_patterns:
                title_match = re.search(pattern, msg)
                if title_match:
                    title = title_match.group(1).strip()
                    break
            
            date_patterns = [
                r"for (?:day )?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                r"on (?:day )?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                r"for (today|tomorrow)",
                r"on (today|tomorrow)",
                r"this (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, msg)
                if date_match:
                    date_str = date_match.group(1).strip()
                    break
            
            logger.info(f"[CALENDAR PARSER] title: {title}, date_str: {date_str}, msg: {msg}")
            
            if context and context.pending_confirmation:
                date_str = context.pending_confirmation
            
            if title and date_str:
                parsed_date = CalendarParser.parse_date(date_str)
                logger.info(f"[CALENDAR PARSER] parsed_date from date_str: {parsed_date}")
                if parsed_date:
                    return {
                        "action": "create_all_day_event",
                        "title": title,
                        "date": parsed_date,
                    }
            
            if title:
                parsed_date = CalendarParser.parse_date(msg)
                logger.info(f"[CALENDAR PARSER] parsed_date from msg: {parsed_date}")
                if parsed_date:
                    return {
                        "action": "create_all_day_event",
                        "title": title,
                        "date": parsed_date,
                    }
            
            if date_str and not title:
                parsed_date = CalendarParser.parse_date(date_str)
                if parsed_date:
                    return {
                        "action": "awaiting_event_title",
                        "date": parsed_date,
                    }
            
            if title:
                return {
                    "action": "awaiting_event_title",
                    "date": datetime.now().date().isoformat(),
                }

        patterns = [
            r"schedule (?:a )?meeting (.+) (?:at|on) (.+)",
            r"schedule (.+) (?:at|on) (.+)",
            r"create (?:an? )?event (.+) (?:at|on) (.+)",
            r"add (.+) (?:at|on) (.+) to my calendar",
            r"book (.+) (?:at|on) (.+)",
            r"plan (.+) (?:at|on) (.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, msg)
            if match:
                title = match.group(1).strip()
                time_str = match.group(2).strip()
                parsed_time = CalendarParser.parse_datetime(time_str)
                if parsed_time:
                    return {
                        "action": "create_event",
                        "title": title,
                        "start_time": parsed_time["start"],
                        "end_time": parsed_time["end"],
                    }

        if "every" in msg and ("monday" in msg or "tuesday" in msg or "wednesday" in msg or 
                               "thursday" in msg or "friday" in msg or "saturday" in msg or "sunday" in msg):
            recur_match = re.search(r"every (\w+) at (.+)", msg)
            if recur_match:
                day_name = recur_match.group(1).strip()
                time_str = recur_match.group(2).strip()
                
                day_map = {
                    "monday": "MO", "tuesday": "TU", "wednesday": "WE",
                    "thursday": "TH", "friday": "FR", "saturday": "SA", "sunday": "SU"
                }
                
                if day_name.lower() in day_map:
                    parsed_time = CalendarParser.parse_datetime(f"next {day_name.lower()} at {time_str}")
                    if parsed_time:
                        rrule = f"FREQ=WEEKLY;BYDAY={day_map[day_name.lower()]}"
                        return {
                            "action": "create_recurring_event",
                            "title": msg.replace("schedule weekly", "").replace("every", "").split("at")[0].strip(),
                            "start_time": parsed_time["start"],
                            "end_time": parsed_time["end"],
                            "recurrence_rule": rrule,
                        }

        return None

    @staticmethod
    def parse_datetime(time_str: str) -> Optional[Dict[str, str]]:
        """Parse natural language datetime."""
        time_str = time_str.lower().strip()
        now = datetime.now()

        day_map = {
            "today": now.date(),
            "tomorrow": (now + timedelta(days=1)).date(),
            "monday": CalendarParser.next_weekday(0),
            "tuesday": CalendarParser.next_weekday(1),
            "wednesday": CalendarParser.next_weekday(2),
            "thursday": CalendarParser.next_weekday(3),
            "friday": CalendarParser.next_weekday(4),
            "saturday": CalendarParser.next_weekday(5),
            "sunday": CalendarParser.next_weekday(6),
        }

        date_obj = None

        if "next " in time_str:
            day_match = re.search(r"next (\w+)", time_str)
            if day_match:
                day_name = day_match.group(1)
                if day_name in day_map:
                    date_obj = CalendarParser.next_weekday(day_map.keys().index(day_name) if day_name in day_map else 0)

        for day_name, day_date in day_map.items():
            if day_name in time_str:
                date_obj = day_date
                break

        if not date_obj:
            # Try parsing patterns like "Mar 14" or "March 14"
            month_match = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})", time_str)
            if month_match:
                month_name = month_match.group(1)
                day = int(month_match.group(2))
                
                months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
                month_idx = months.index(month_name) + 1
                
                # Check if year is in string
                year_match = re.search(r"\b(20\d{2})\b", time_str)
                year = int(year_match.group(1)) if year_match else now.year
                
                try:
                    date_obj = datetime(year, month_idx, day).date()
                    # If date is in the past and no year was specified, assume next year
                    if not year_match and date_obj < now.date():
                        date_obj = datetime(year + 1, month_idx, day).date()
                except ValueError:
                    pass

        if not date_obj:
            date_obj = now.date()

        # Look for time: prioritize patterns with colons or AM/PM to avoid matching date numbers
        time_match = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)?|(\d{1,2})\s*(am|pm)", time_str)
        if time_match:
            if time_match.group(1): # Pattern with colon
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                ampm = time_match.group(3)
            else: # Pattern with just AM/PM
                hour = int(time_match.group(4))
                minute = 0
                ampm = time_match.group(5)

            if "evening" in time_str or "night" in time_str:
                if hour < 12 and ampm != "am":
                    hour += 12
            elif "afternoon" in time_str and (ampm is None or ampm == "pm"):
                if hour < 12:
                    hour += 12 if hour != 12 else 12
            elif "morning" in time_str and ampm == "pm":
                pass
            else:
                if ampm == "pm" and hour != 12:
                    hour += 12
                elif ampm == "am" and hour == 12:
                    hour = 0

            start_dt = datetime.combine(date_obj, datetime.min.time().replace(hour=hour, minute=minute))
            end_dt = start_dt + timedelta(hours=1)

            return {
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
            }

        return None

    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        """Parse natural language date."""
        date_str = date_str.lower().strip()
        now = datetime.now()

        day_map = {
            "today": now.date(),
            "tomorrow": (now + timedelta(days=1)).date(),
            "monday": CalendarParser.next_weekday(0),
            "tuesday": CalendarParser.next_weekday(1),
            "wednesday": CalendarParser.next_weekday(2),
            "thursday": CalendarParser.next_weekday(3),
            "friday": CalendarParser.next_weekday(4),
            "saturday": CalendarParser.next_weekday(5),
            "sunday": CalendarParser.next_weekday(6),
        }

        for day_name, day_date in day_map.items():
            if day_name in date_str:
                return day_date.isoformat()

        if "this weekend" in date_str:
            return CalendarParser.next_weekday(5).isoformat()

        return None

    @staticmethod
    def next_weekday(weekday: int) -> datetime.date:
        """Get next occurrence of a weekday."""
        now = datetime.now()
        days_ahead = weekday - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (now + timedelta(days_ahead)).date()

    @staticmethod
    def parse_list_events(message: str) -> Optional[Dict[str, Any]]:
        """Parse list events message."""
        msg = message.lower()

        if "what's on my calendar" in msg or "whats on my calendar" in msg:
            if "today" in msg:
                return {"action": "list_today"}
            elif "tomorrow" in msg:
                return {"action": "list_tomorrow"}
            elif "week" in msg:
                return {"action": "list_week"}
            else:
                return {"action": "list_upcoming"}

        if "show my meetings" in msg or "show events" in msg:
            if "today" in msg:
                return {"action": "list_today"}
            elif "tomorrow" in msg:
                return {"action": "list_tomorrow"}
            elif "week" in msg:
                return {"action": "list_week"}

        return None

    @staticmethod
    def parse_delete_event(message: str) -> Optional[Dict[str, Any]]:
        """Parse delete event message."""
        msg = message.lower()

        if "cancel" in msg or "delete" in msg:
            # Check for "cancel this meeting: [details]" or "cancel [details]"
            detail_patterns = [
                r"cancel this meeting:\s*(.+)",
                r"cancel the meeting:\s*(.+)",
                r"cancel meeting:\s*(.+)",
                r"cancel\s+(.+ meeting with .+)$",
                r"cancel\s+(.+ interview with .+)$",
            ]
            
            for pattern in detail_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    query = match.group(1).strip()
                    return {"action": "delete_event", "query": query}

            id_match = re.search(r"(\d+)", message)
            if id_match:
                return {"action": "delete_event", "event_id": id_match.group(1)}

            time_match = re.search(r"(?:at |on )?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", msg)
            if time_match:
                return {"action": "delete_by_time", "time": time_match.group(1)}
            
            # Default fallback for "cancel [something]"
            match = re.search(r"(?:cancel|delete)\s+(.+)", message, re.IGNORECASE)
            if match:
                return {"action": "delete_event", "query": match.group(1).strip()}

        return None

    @staticmethod
    def parse_search_events(message: str) -> Optional[Dict[str, Any]]:
        """Parse search events message."""
        msg = message.lower()

        search_patterns = [
            r"when (?:is|was) (.+) meeting",
            r"find (.+) meeting",
            r"search (.+) meeting",
            r"search for (.+)",
        ]

        for pattern in search_patterns:
            match = re.search(pattern, msg)
            if match:
                query = match.group(1).strip()
                return {"action": "search_events", "query": query}

        return None

    @staticmethod
    def parse_modify_event(message: str) -> Optional[Dict[str, Any]]:
        """Parse modify event message."""
        msg = message.lower()

        if "move" in msg and "to" in msg:
            time_match = re.search(r"to (\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", msg)
            if time_match:
                new_time = time_match.group(1)
                parsed_time = CalendarParser.parse_datetime(f"tomorrow at {new_time}")
                if parsed_time:
                    return {
                        "action": "reschedule_event",
                        "new_start": parsed_time["start"],
                        "new_end": parsed_time["end"],
                    }

        if "add" in msg and "@" in message:
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", message)
            if email_match:
                return {
                    "action": "add_attendee",
                    "email": email_match.group(0),
                }

        if "rename" in msg or "change name" in msg:
            title_match = re.search(r"to (.+?)(?:$|\?)", msg)
            if title_match:
                return {
                    "action": "change_title",
                    "new_title": title_match.group(1).strip(),
                }

        return None

    @staticmethod
    def parse_availability_check(message: str) -> Optional[Dict[str, Any]]:
        """Parse availability check message."""
        msg = message.lower()

        if "am i free" in msg or "do i have time" in msg:
            time_match = re.search(r"(?:at |between )?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", msg)
            if time_match:
                time_str = time_match.group(1)
                parsed_time = CalendarParser.parse_datetime(f"tomorrow at {time_str}")
                if parsed_time:
                    return {
                        "action": "check_specific_time",
                        "time_min": parsed_time["start"],
                        "time_max": parsed_time["end"],
                    }

        return None

    @staticmethod
    def parse_find_slots(message: str) -> Optional[Dict[str, Any]]:
        """Parse find slots message."""
        msg = message.lower()

        if "find" in msg and ("slot" in msg or "time" in msg):
            duration = 30
            duration_match = re.search(r"(\d+)\s*minute", msg)
            if duration_match:
                duration = int(duration_match.group(1))

            date_str = "tomorrow"
            if "today" in msg:
                date_str = "today"
            elif "friday" in msg or "monday" in msg:
                parsed = CalendarParser.parse_date(msg)
                if parsed:
                    date_str = parsed

            return {
                "action": "find_slots",
                "date_str": date_str,
                "duration_minutes": duration,
            }

        return None


def parse_calendar_message(message: str, context: Optional["ConversationContext"] = None) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Parse calendar-related message and return action."""
    msg = message.lower().strip()

    parser = CalendarParser()

    create_result = parser.parse_create_event(message, context)
    if create_result:
        if create_result.get("action") == "awaiting_event_title":
            return "calendar_need_more_info", create_result
        return "calendar", create_result

    list_result = parser.parse_list_events(message)
    if list_result:
        return "calendar", list_result

    delete_result = parser.parse_delete_event(message)
    if delete_result:
        return "calendar", delete_result

    search_result = parser.parse_search_events(message)
    if search_result:
        return "calendar", search_result

    modify_result = parser.parse_modify_event(message)
    if modify_result:
        return "calendar", modify_result

    availability_result = parser.parse_availability_check(message)
    if availability_result:
        return "calendar", availability_result

    slots_result = parser.parse_find_slots(message)
    if slots_result:
        return "calendar", slots_result

    if "free" in msg or "available" in msg or "busy" in msg:
        return "calendar", {"action": "check_availability"}

    if "find slot" in msg or "suggest meeting" in msg:
        return "calendar", {"action": "find_slots"}

    return "general", None
