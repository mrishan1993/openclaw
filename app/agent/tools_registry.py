"""Tools registry for the AI agent."""
from typing import Dict, Any, Callable, List, Optional
from app.tools import task_tools, note_tools
from app.calendar import calendar_tools


TOOLS_REGISTRY: Dict[str, Callable] = {
    "save_task": task_tools.save_task,
    "get_today_tasks": task_tools.get_today_tasks,
    "get_all_tasks": task_tools.get_all_tasks,
    "delete_task": task_tools.delete_task,
    "complete_task": task_tools.complete_task,
    "delete_all_tasks": task_tools.delete_all_tasks,
    "save_note": note_tools.save_note,
    "search_notes": note_tools.search_notes,
    "get_recent_notes": note_tools.get_recent_notes,
    "get_all_notes": note_tools.get_all_notes,
    "delete_note": note_tools.delete_note,
    "delete_all_notes": note_tools.delete_all_notes,
    "create_event": calendar_tools.create_event,
    "create_all_day_event": calendar_tools.create_all_day_event,
    "create_recurring_event": calendar_tools.create_recurring_event,
    "list_today_events": calendar_tools.list_today_events,
    "list_tomorrow_events": calendar_tools.list_tomorrow_events,
    "list_upcoming_events": calendar_tools.list_upcoming_events,
    "list_events_by_date": calendar_tools.list_events_by_date,
    "list_week_events": calendar_tools.list_week_events,
    "get_event_details": calendar_tools.get_event_details,
    "delete_event": calendar_tools.delete_event,
    "search_events": calendar_tools.search_events,
    "check_availability": calendar_tools.check_availability,
    "find_free_slots": calendar_tools.find_free_slots,
    "reschedule_event": calendar_tools.reschedule_event,
    "change_event_title": calendar_tools.change_event_title,
    "add_event_attendee": calendar_tools.add_event_attendee,
    "remove_event_attendee": calendar_tools.remove_event_attendee,
    "list_event_attendees": calendar_tools.list_event_attendees,
    "check_specific_time": calendar_tools.check_specific_time,
    "cancel_recurring_instance": calendar_tools.cancel_recurring_instance,
    "cancel_recurring_series": calendar_tools.cancel_recurring_series,
    "get_meeting_link": calendar_tools.get_meeting_link,
    "add_meeting_link": calendar_tools.add_meeting_link,
    "add_reminder": calendar_tools.add_reminder,
    "update_reminder": calendar_tools.update_reminder,
    "remove_reminder": calendar_tools.remove_reminder,
    "get_daily_agenda": calendar_tools.get_daily_agenda,
}


TOOL_DESCRIPTIONS = {
    "save_task": {
        "name": "save_task",
        "description": "Save a new task. Use when user wants to add a task.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The task title"},
                "due_time": {
                    "type": "string",
                    "description": "Optional due time in ISO format",
                },
            },
            "required": ["title"],
        },
    },
    "get_today_tasks": {
        "name": "get_today_tasks",
        "description": "Get all tasks for today.",
        "parameters": {"type": "object", "properties": {}},
    },
    "get_all_tasks": {
        "name": "get_all_tasks",
        "description": "Get all pending tasks.",
        "parameters": {"type": "object", "properties": {}},
    },
    "save_note": {
        "name": "save_note",
        "description": "Save a new note. Use when user wants to save a note or idea.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The note content"},
                "tags": {
                    "type": "string",
                    "description": "Optional comma-separated tags",
                },
            },
            "required": ["content"],
        },
    },
    "search_notes": {
        "name": "search_notes",
        "description": "Search notes by query. Use when user asks about specific topics.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
            },
            "required": ["query"],
        },
    },
    "get_recent_notes": {
        "name": "get_recent_notes",
        "description": "Get recent notes.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of notes",
                    "default": 5,
                },
            },
        },
    },
    "get_all_notes": {
        "name": "get_all_notes",
        "description": "Get all notes. Use when user wants to see all notes.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of notes",
                    "default": 50,
                },
            },
        },
    },
    "delete_task": {
        "name": "delete_task",
        "description": "Delete a task by ID. Use when user wants to remove a task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The task ID to delete"},
            },
            "required": ["task_id"],
        },
    },
    "complete_task": {
        "name": "complete_task",
        "description": "Mark a task as completed. Use when user wants to mark done.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The task ID to complete"},
            },
            "required": ["task_id"],
        },
    },
    "delete_note": {
        "name": "delete_note",
        "description": "Delete a note by ID. Use when user wants to delete a note.",
        "parameters": {
            "type": "object",
            "properties": {
                "note_id": {"type": "integer", "description": "The note ID to delete"},
            },
            "required": ["note_id"],
        },
    },
    "delete_all_tasks": {
        "name": "delete_all_tasks",
        "description": "Delete all tasks. Use when user wants to delete all tasks.",
        "parameters": {"type": "object", "properties": {}},
    },
    "delete_all_notes": {
        "name": "delete_all_notes",
        "description": "Delete all notes. Use when user wants to delete all notes.",
        "parameters": {"type": "object", "properties": {}},
    },
    "create_event": {
        "name": "create_event",
        "description": "Create a new calendar event with specific time. Use when user wants to schedule a meeting or event.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title or meeting name"},
                "start_time": {"type": "string", "description": "Start time in ISO format"},
                "end_time": {"type": "string", "description": "End time in ISO format"},
                "description": {"type": "string", "description": "Optional event description"},
                "location": {"type": "string", "description": "Optional location"},
                "attendees": {"type": "string", "description": "Optional comma-separated list of attendee email addresses"},
            },
            "required": ["title", "start_time", "end_time"],
        },
    },
    "create_all_day_event": {
        "name": "create_all_day_event",
        "description": "Create an all-day event. Use when user wants to create a day-long event.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "description": {"type": "string", "description": "Optional description"},
            },
            "required": ["title", "date"],
        },
    },
    "create_recurring_event": {
        "name": "create_recurring_event",
        "description": "Create a recurring event. Use for weekly meetings or daily standups.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title"},
                "start_time": {"type": "string", "description": "Start time in ISO format"},
                "end_time": {"type": "string", "description": "End time in ISO format"},
                "recurrence_rule": {"type": "string", "description": "RRULE format (e.g., 'FREQ=WEEKLY;BYDAY=MO')"},
                "description": {"type": "string", "description": "Optional description"},
                "location": {"type": "string", "description": "Optional location"},
                "attendees": {"type": "string", "description": "Optional comma-separated list of attendee email addresses"},
            },
            "required": ["title", "start_time", "end_time", "recurrence_rule"],
        },
    },
    "list_today_events": {
        "name": "list_today_events",
        "description": "Get today's calendar events. Use when user asks about today's schedule.",
        "parameters": {"type": "object", "properties": {}},
    },
    "list_tomorrow_events": {
        "name": "list_tomorrow_events",
        "description": "Get tomorrow's calendar events.",
        "parameters": {"type": "object", "properties": {}},
    },
    "list_upcoming_events": {
        "name": "list_upcoming_events",
        "description": "Get upcoming events. Use when user wants to see future meetings.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Maximum number of events", "default": 10},
            },
        },
    },
    "list_events_by_date": {
        "name": "list_events_by_date",
        "description": "Get events for a specific date. Use when user asks about a specific day.",
        "parameters": {
            "type": "object",
            "properties": {
                "date_str": {"type": "string", "description": "Date string (today, tomorrow, or date)"},
            },
            "required": ["date_str"],
        },
    },
    "list_week_events": {
        "name": "list_week_events",
        "description": "Get this week's events.",
        "parameters": {"type": "object", "properties": {}},
    },
    "get_event_details": {
        "name": "get_event_details",
        "description": "Get detailed information about a specific event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
            },
            "required": ["event_id"],
        },
    },
    "delete_event": {
        "name": "delete_event",
        "description": "Delete a calendar event. Use when user wants to cancel or remove an event.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search string to match the event to cancel, including title, date, or time."},
            },
            "required": ["query"],
        },
    },
    "search_events": {
        "name": "search_events",
        "description": "Search calendar events by keyword. Use when user wants to find specific meetings.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        },
    },
    "check_availability": {
        "name": "check_availability",
        "description": "Check if user is free on a given day.",
        "parameters": {
            "type": "object",
            "properties": {
                "date_str": {"type": "string", "description": "Date to check (today or tomorrow)", "default": "today"},
            },
        },
    },
    "find_free_slots": {
        "name": "find_free_slots",
        "description": "Find available time slots for scheduling between two explicit times.",
        "parameters": {
            "type": "object",
            "properties": {
                "time_min_str": {"type": "string", "description": "Lower bound time in ISO format (e.g. 2026-03-12T09:00:00+05:30)"},
                "time_max_str": {"type": "string", "description": "Upper bound time in ISO format (e.g. 2026-03-12T17:00:00+05:30)"},
                "duration_minutes": {"type": "integer", "description": "Meeting duration in minutes", "default": 30},
            },
            "required": ["time_min_str", "time_max_str"],
        },
    },
    "reschedule_event": {
        "name": "reschedule_event",
        "description": "Change the time of an existing event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "new_start": {"type": "string", "description": "New start time in ISO format"},
                "new_end": {"type": "string", "description": "New end time in ISO format"},
            },
            "required": ["event_id", "new_start", "new_end"],
        },
    },
    "change_event_title": {
        "name": "change_event_title",
        "description": "Rename an existing event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "new_title": {"type": "string", "description": "New event title"},
            },
            "required": ["event_id", "new_title"],
        },
    },
    "add_event_attendee": {
        "name": "add_event_attendee",
        "description": "Add an attendee to an existing event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "email": {"type": "string", "description": "Attendee email address"},
            },
            "required": ["event_id", "email"],
        },
    },
    "remove_event_attendee": {
        "name": "remove_event_attendee",
        "description": "Remove an attendee from an existing event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "email": {"type": "string", "description": "Attendee email address to remove"},
            },
            "required": ["event_id", "email"],
        },
    },
    "list_event_attendees": {
        "name": "list_event_attendees",
        "description": "List all attendees for an existing event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
            },
            "required": ["event_id"],
        },
    },
    "check_specific_time": {
        "name": "check_specific_time",
        "description": "Check if a specific time slot is free.",
        "parameters": {
            "type": "object",
            "properties": {
                "time_min": {"type": "string", "description": "Start time in ISO format"},
                "time_max": {"type": "string", "description": "End time in ISO format"},
            },
            "required": ["time_min", "time_max"],
        },
    },
    "cancel_recurring_instance": {
        "name": "cancel_recurring_instance",
        "description": "Cancel a single occurrence of a recurring meeting given its instance event ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Instance event ID to cancel"},
            },
            "required": ["event_id"],
        },
    },
    "cancel_recurring_series": {
        "name": "cancel_recurring_series",
        "description": "Cancel an entire recurring meeting series given any instance or the master event ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID belonging to the series"},
            },
            "required": ["event_id"],
        },
    },
    "get_meeting_link": {
        "name": "get_meeting_link",
        "description": "Get the primary meeting link for an event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
            },
            "required": ["event_id"],
        },
    },
    "add_meeting_link": {
        "name": "add_meeting_link",
        "description": "Attach a meeting link (Google Meet, Zoom, Teams, or custom URL) to an event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "platform": {
                    "type": "string",
                    "description": "Platform name (google_meet, zoom, teams, custom)",
                    "default": "google_meet",
                },
                "url": {
                    "type": "string",
                    "description": "Meeting URL (required for non-Google Meet platforms)",
                },
            },
            "required": ["event_id"],
        },
    },
    "add_reminder": {
        "name": "add_reminder",
        "description": "Add a reminder before a meeting.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "minutes_before": {
                    "type": "integer",
                    "description": "Minutes before event start to trigger the reminder",
                },
                "method": {
                    "type": "string",
                    "description": "Reminder method (popup, email, sms)",
                    "default": "popup",
                },
            },
            "required": ["event_id", "minutes_before"],
        },
    },
    "update_reminder": {
        "name": "update_reminder",
        "description": "Update an existing reminder for an event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "index": {
                    "type": "integer",
                    "description": "Zero-based index of the reminder to update",
                },
                "minutes_before": {
                    "type": "integer",
                    "description": "New minutes before event start",
                },
                "method": {
                    "type": "string",
                    "description": "Optional new reminder method",
                },
            },
            "required": ["event_id", "index", "minutes_before"],
        },
    },
    "remove_reminder": {
        "name": "remove_reminder",
        "description": "Remove one or all reminders from an event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID"},
                "index": {
                    "type": ["integer", "null"],
                    "description": "Zero-based index of the reminder to remove; omit to remove all",
                },
            },
            "required": ["event_id"],
        },
    },
    "get_daily_agenda": {
        "name": "get_daily_agenda",
        "description": "Get a formatted agenda for today's schedule, including overlapping events and all-day events.",
        "parameters": {"type": "object", "properties": {}},
    },
}


def get_tool(name: str) -> Callable:
    """Get a tool by name."""
    return TOOLS_REGISTRY.get(name)


def get_all_tools() -> List[Dict[str, Any]]:
    """Get all available tools."""
    return list(TOOL_DESCRIPTIONS.values())


def execute_tool(name: str, phone_number: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Execute a tool by name with given arguments."""
    tool = get_tool(name)
    if not tool:
        return {"success": False, "message": f"Tool '{name}' not found"}
    
    # Check if tool accepts phone_number
    import inspect
    sig = inspect.signature(tool)
    if "phone_number" in sig.parameters:
        kwargs["phone_number"] = phone_number
        
    try:
        return tool(**kwargs)
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return {"success": False, "message": str(e)}
