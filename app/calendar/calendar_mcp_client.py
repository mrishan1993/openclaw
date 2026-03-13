"""Google Calendar API client."""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import urllib.parse

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

GOOGLE_CALENDAR_API_URL = "https://www.googleapis.com/calendar/v3"


class CalendarClient:
    """Client for Google Calendar API operations."""

    def __init__(self, access_token: Optional[str] = None):
        """Initialize the calendar client with optional user-specific token."""
        self._access_token = access_token or settings.google_access_token

    @property
    def token(self) -> str:
        """Get the access token."""
        if not self._access_token:
            raise ValueError("No Google access token available. User must authenticate first.")
        return self._access_token

    def set_access_token(self, access_token: str) -> None:
        """Set a new access token (for user-specific operations)."""
        self._access_token = access_token

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Google Calendar API."""
        url = f"{GOOGLE_CALENDAR_API_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                if method == "GET":
                    response = client.get(url, headers=headers)
                elif method == "POST":
                    response = client.post(url, headers=headers, json=data)
                elif method == "PUT":
                    response = client.put(url, headers=headers, json=data)
                elif method == "PATCH":
                    response = client.patch(url, headers=headers, json=data)
                elif method == "DELETE":
                    response = client.delete(url, headers=headers)
                else:
                    return {"success": False, "error": f"Unknown method: {method}"}

                logger.info(f"API Response status: {response.status_code}, body: {response.text[:500] if response.text else 'empty'}")
                
                if response.status_code == 404:
                    return {"success": False, "error": "Not found", "status": 404}
                
                if response.status_code == 401:
                    return {"success": False, "error": "Unauthorized - token may be expired", "status": 401}
                
                if response.status_code == 403:
                    return {"success": False, "error": "Forbidden - check permissions", "status": 403}
                
                response.raise_for_status()
                
                if not response.text or response.status_code == 204:
                    return {"success": True, "data": {}}
                
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            logger.error(f"Calendar API error: {e.response.status_code} - {e.response.text}")
            return {"success": False, "error": f"API error: {e.response.status_code}"}
        except httpx.ConnectError:
            logger.error("Calendar API connection failed - check internet connection")
            return {"success": False, "error": "Connection failed"}
        except Exception as e:
            logger.error(f"Error calling Calendar API: {e}")
            return {"success": False, "error": str(e)}

    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: str = "",
        attendees: List[str] = None,
        location: str = ""
    ) -> Dict[str, Any]:
        """Create a calendar event."""
        data = {
            "summary": title,
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
            "description": description,
            "location": location,
            "sendUpdates": "all",
        }
        if attendees:
            data["attendees"] = [{"email": email} for email in attendees]

        result = self._make_request("POST", "/calendars/primary/events?sendUpdates=all", data)
        if result.get("success"):
            event = result.get("data", {})
            return {
                "success": True,
                "message": f"Event created: {event.get('summary')}",
                "event_id": event.get("id"),
                "event": event,
            }
        return {"success": False, "message": f"Failed to create event: {result.get('error')}"}

    def create_all_day_event(self, title: str, date: str, description: str = "") -> Dict[str, Any]:
        """Create an all-day event."""
        data = {
            "summary": title,
            "start": {"date": date, "timeZone": "Asia/Kolkata"},
            "end": {"date": date, "timeZone": "Asia/Kolkata"},
            "description": description,
            "sendUpdates": "all",
        }

        result = self._make_request("POST", "/calendars/primary/events?sendUpdates=all", data)
        if result.get("success"):
            event = result.get("data", {})
            return {
                "success": True,
                "message": f"All-day event created: {event.get('summary')}",
                "event_id": event.get("id"),
                "event": event,
            }
        return {"success": False, "message": f"Failed to create event: {result.get('error')}"}

    def list_events(self, max_results: int = 10, time_min: str = None, time_max: str = None) -> Dict[str, Any]:
        """List upcoming events."""
        params = f"maxResults={max_results}&singleEvents=true&orderBy=startTime"
        if time_min:
            params += f"&timeMin={urllib.parse.quote(time_min, safe='')}"
        if time_max:
            params += f"&timeMax={urllib.parse.quote(time_max, safe='')}"
        
        logger.info(f"Listing events with params: {params}")

        result = self._make_request("GET", f"/calendars/primary/events?{params}")
        if result.get("success"):
            events = result.get("data", {}).get("items", [])
            return {
                "success": True,
                "events": events,
                "count": len(events),
            }
        return {"success": False, "message": f"Failed to list events: {result.get('error')}"}

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get event details."""
        result = self._make_request("GET", f"/calendars/primary/events/{event_id}")
        if result.get("success"):
            return {"success": True, "event": result.get("data")}
        return {"success": False, "message": f"Failed to get event: {result.get('error')}"}

    def update_event(self, event_id: str, updates: Dict) -> Dict[str, Any]:
        """Update an event."""
        result = self._make_request("PUT", f"/calendars/primary/events/{event_id}?sendUpdates=all", updates)
        if result.get("success"):
            return {
                "success": True,
                "message": "Event updated",
                "event": result.get("data"),
            }
        return {"success": False, "message": f"Failed to update event: {result.get('error')}"}

    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete an event."""
        result = self._make_request("DELETE", f"/calendars/primary/events/{event_id}?sendUpdates=all")
        if result.get("success"):
            return {"success": True, "message": "Event deleted"}
        return {"success": False, "message": f"Failed to delete event: {result.get('error')}"}

    def search_events(self, query: str, time_min: Optional[str] = None) -> Dict[str, Any]:
        """Search events by query."""
        params = f"q={urllib.parse.quote(query, safe='')}&maxResults=10"
        if time_min:
            params += f"&timeMin={urllib.parse.quote(time_min, safe='')}"
        result = self._make_request("GET", f"/calendars/primary/events?{params}")
        if result.get("success"):
            events = result.get("data", {}).get("items", [])
            return {
                "success": True,
                "events": events,
                "count": len(events),
            }
        return {"success": False, "message": f"Failed to search events: {result.get('error')}"}

    def check_free_busy(self, time_min: str, time_max: str) -> Dict[str, Any]:
        """Check free/busy status."""
        data = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": "primary"}],
        }

        result = self._make_request("POST", "/freeBusy", data)
        if result.get("success"):
            return {"success": True, "data": result.get("data")}
        return {"success": False, "message": f"Failed to check availability: {result.get('error')}"}

    def create_recurring_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        recurrence_rule: str,
        description: str = "",
        attendees: List[str] = None,
        location: str = ""
    ) -> Dict[str, Any]:
        """Create a recurring calendar event."""
        data = {
            "summary": title,
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
            "description": description,
            "location": location,
            "recurrence": [recurrence_rule],
        }
        if attendees:
            data["attendees"] = [{"email": email} for email in attendees]

        result = self._make_request("POST", "/calendars/primary/events", data)
        if result.get("success"):
            event = result.get("data", {})
            return {
                "success": True,
                "message": f"Recurring event created: {event.get('summary')}",
                "event_id": event.get("id"),
                "event": event,
            }
        return {"success": False, "message": f"Failed to create recurring event: {result.get('error')}"}

    def add_attendee_to_event(self, event_id: str, email: str) -> Dict[str, Any]:
        """Add an attendee to an existing event."""
        event_result = self.get_event(event_id)
        if not event_result.get("success"):
            return {"success": False, "message": "Event not found"}

        event = event_result.get("event", {})
        attendees = event.get("attendees", [])
        attendees.append({"email": email})

        updates = {"attendees": attendees}
        return self.update_event(event_id, updates)

    def remove_attendee_from_event(self, event_id: str, email: str) -> Dict[str, Any]:
        """Remove an attendee from an existing event."""
        event_result = self.get_event(event_id)
        if not event_result.get("success"):
            return {"success": False, "message": "Event not found"}

        event = event_result.get("event", {})
        attendees = event.get("attendees", [])
        attendees = [a for a in attendees if a.get("email") != email]

        updates = {"attendees": attendees}
        return self.update_event(event_id, updates)

    def reschedule_event(self, event_id: str, new_start: str, new_end: str) -> Dict[str, Any]:
        """Reschedule an event to new times."""
        updates = {
            "start": {"dateTime": new_start, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": new_end, "timeZone": "Asia/Kolkata"},
        }
        return self.update_event(event_id, updates)

    def change_event_title(self, event_id: str, new_title: str) -> Dict[str, Any]:
        """Change the title of an event."""
        updates = {"summary": new_title}
        return self.update_event(event_id, updates)

    def update_event_reminders(
        self,
        event_id: str,
        overrides: Optional[List[Dict[str, Any]]] = None,
        use_default: bool = False,
    ) -> Dict[str, Any]:
        """Update reminder settings for an event."""
        updates: Dict[str, Any] = {
            "reminders": {
                "useDefault": use_default,
            }
        }
        if overrides is not None:
            updates["reminders"]["overrides"] = overrides

        return self.update_event(event_id, updates)

    def patch_event_with_conference_data(self, event_id: str, conference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attach or update conferenceData for an event (e.g., Google Meet link)."""
        data = {"conferenceData": conference_data}
        result = self._make_request(
            "PATCH",
            f"/calendars/primary/events/{event_id}?conferenceDataVersion=1&sendUpdates=all",
            data,
        )
        if result.get("success"):
            return {
                "success": True,
                "message": "Event updated",
                "event": result.get("data"),
            }
        return {"success": False, "message": f"Failed to update event: {result.get('error')}"}


calendar_client = CalendarClient()
