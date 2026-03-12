"""AI Agent for processing WhatsApp messages."""
import json
import re
from typing import Dict, Any, Optional

import httpx

from app.config import get_settings
from app.agent.prompts import SYSTEM_PROMPT, format_task_response, format_note_response
from app.agent.tools_registry import execute_tool, get_all_tools
from app.utils.logger import get_logger

logger = get_logger(__name__)

settings = get_settings()


class Agent:
    """AI Agent for processing user messages."""

    def __init__(self):
        """Initialize the agent."""
        self.tools = get_all_tools()
        self.system_prompt = SYSTEM_PROMPT

    def _build_messages(self, user_message: str, context=None) -> list:
        """Build message list for OpenClaw API."""
        from datetime import datetime
        
        # Inject current time so the LLM doesn't hallucinate dates
        current_time = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S (Asia/Kolkata)")
        dynamic_system_prompt = f"{self.system_prompt}\n\nThe current date and time is: {current_time}."
        
        messages = [{"role": "system", "content": dynamic_system_prompt}]
        
        if context and hasattr(context, 'history') and context.history:
            # Add up to the last 10 messages from history to provide context
            # The most recent message should be the user message itself
            recent_history = context.history[-10:]
            for msg in recent_history:
                # The stored history might have 'timestamp', we only want 'role' and 'content' for OpenAI
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        else:
            messages.append({"role": "user", "content": user_message})
            
        return messages

    def _call_openclaw(self, messages: list) -> Optional[Dict[str, Any]]:
        """Call OpenClaw API to get agent response."""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openclaw_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": messages,
                        "tools": [
                            {"type": "function", "function": tool}
                            for tool in self.tools
                        ],
                        "max_tokens": 1000,
                    },
                )
                if response.status_code != 200:
                    logger.error(f"OpenAI API response body: {response.text}")
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error("OpenClaw API timeout")
            return None
        except httpx.HTTPError as e:
            logger.error(f"OpenClaw API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling OpenClaw: {e}")
            return None

    def _parse_tool_calls(self, response: Dict[str, Any]) -> list:
        """Parse tool calls from OpenClaw response."""
        try:
            choices = response.get("choices", [])
            if not choices:
                return []

            message = choices[0].get("message", {})
            tool_calls = message.get("tool_calls", [])

            parsed = []
            for call in tool_calls:
                func = call.get("function", {})
                parsed.append({
                    "name": func.get("name"),
                    "arguments": json.loads(func.get("arguments", "{}")),
                })
            return parsed
        except Exception as e:
            logger.error(f"Error parsing tool calls: {e}")
            return []

    def process_message(self, user_message: str, context=None) -> str:
        """Process user message and return response."""
        logger.info(f"Processing message: {user_message}")

        messages = self._build_messages(user_message, context)
        response = self._call_openclaw(messages)

        if not response:
            return self._fallback_response(user_message, context)

        tool_calls = self._parse_tool_calls(response)

        if not tool_calls:
            choices = response.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
                if content:
                    return content

        tool_results = []
        for call in tool_calls:
            logger.info(f"Executing tool: {call['name']}")
            result = execute_tool(call["name"], **call["arguments"])
            tool_results.append(result)

        return self._format_response(tool_results, tool_calls)

    def _format_response(
        self, tool_results: list, tool_calls: list
    ) -> str:
        """Format tool results into user-friendly response."""
        if not tool_results:
            return "I understand your message."

        responses = []
        for i, result in enumerate(tool_results):
            if not result.get("success", False):
                responses.append(result.get("message", "Something went wrong"))
                continue

            tool_name = tool_calls[i]["name"] if i < len(tool_calls) else ""

            if tool_name == "save_task":
                responses.append("Added to tasks.")
            elif tool_name == "save_note":
                responses.append("Saved.")
            elif tool_name == "get_today_tasks":
                responses.append(format_task_response(result.get("tasks", [])))
            elif tool_name == "search_notes":
                responses.append(format_note_response(result.get("notes", [])))
            elif tool_name == "get_recent_notes":
                responses.append(format_note_response(result.get("notes", [])))
            elif tool_name == "get_all_tasks":
                responses.append(format_task_response(result.get("tasks", [])))
            elif tool_name == "get_all_notes":
                responses.append(format_note_response(result.get("notes", [])))
            elif tool_name == "delete_task":
                responses.append(result.get("message", "Task deleted."))
            elif tool_name == "complete_task":
                responses.append(result.get("message", "Task completed!"))
            elif tool_name == "delete_note":
                responses.append(result.get("message", "Note deleted."))
            elif tool_name == "delete_all_tasks":
                responses.append(result.get("message", "All tasks deleted."))
            elif tool_name == "delete_all_notes":
                responses.append(result.get("message", "All notes deleted."))
            elif tool_name in ["create_event", "create_all_day_event", "create_recurring_event"]:
                responses.append(result.get("message", "Event created."))
            elif tool_name in ["list_today_events", "list_tomorrow_events", "list_upcoming_events", "list_events_by_date", "list_week_events"]:
                responses.append(result.get("message", "No events found."))
            elif tool_name == "get_event_details":
                responses.append(result.get("message", ""))
            elif tool_name == "delete_event":
                responses.append(result.get("message", "Event deleted."))
            elif tool_name == "search_events":
                responses.append(result.get("message", "No events found."))
            elif tool_name == "check_availability":
                responses.append(result.get("message", "Could not check availability."))
            elif tool_name == "find_free_slots":
                responses.append(result.get("message", "No available slots."))
            elif tool_name == "reschedule_event":
                responses.append(result.get("message", "Event rescheduled."))
            elif tool_name == "change_event_title":
                responses.append(result.get("message", "Event renamed."))
            elif tool_name == "add_event_attendee":
                responses.append(result.get("message", "Attendee added."))
            elif tool_name == "remove_event_attendee":
                responses.append(result.get("message", "Attendee removed."))
            elif tool_name == "check_specific_time":
                responses.append(result.get("message", ""))
            else:
                responses.append("Done.")

        return " ".join(responses)

    def _fallback_response(self, message: str, context=None) -> str:
        """Simple rule-based fallback when OpenClaw API is unavailable."""
        import re
        from app.services.conversation_service import update_conversation_context

        msg = message.lower().strip()

        # Calendar commands
        from app.calendar.calendar_parser import parse_calendar_message
        category, calendar_action = parse_calendar_message(message, context)
        
        if category == "calendar" and calendar_action:
            from app.calendar import calendar_tools
            action = calendar_action.get("action")
            
            if action == "create_event":
                result = calendar_tools.create_event(
                    title=calendar_action.get("title", "Meeting"),
                    start_time=calendar_action.get("start_time"),
                    end_time=calendar_action.get("end_time"),
                )
                return result.get("message", "Event created.")
            
            elif action == "create_all_day_event":
                result = calendar_tools.create_all_day_event(
                    title=calendar_action.get("title", "Event"),
                    date=calendar_action.get("date"),
                )
                return result.get("message", "All-day event created.")
            
            elif action == "list_today":
                result = calendar_tools.list_today_events()
                return result.get("message", "No events today.")
            
            elif action == "list_tomorrow":
                result = calendar_tools.list_tomorrow_events()
                return result.get("message", "No events tomorrow.")
            
            elif action == "list_upcoming" or action == "list_week":
                result = calendar_tools.list_upcoming_events()
                return result.get("message", "No upcoming events.")
            
            elif action == "search_events":
                result = calendar_tools.search_events(calendar_action.get("query", ""))
                return result.get("message", "No events found.")
            
            elif action == "delete_event" or action == "delete_by_time":
                return "Please specify the event ID to delete."
            
            elif action == "check_availability":
                result = calendar_tools.check_availability()
                return result.get("message", "Could not check availability.")
            
            elif action == "find_slots" or action == "find_slot":
                result = calendar_tools.find_free_slots(
                    date_str=calendar_action.get("date_str", "tomorrow"),
                    duration_minutes=calendar_action.get("duration_minutes", 30),
                )
                return result.get("message", "No slots available.")
            
            elif action == "reschedule_event":
                return "Please provide the event ID to reschedule."
            
            elif action == "add_attendee":
                return "Please provide the event ID and email."
            
            elif action == "change_title":
                return "Please provide the event ID and new title."
            
            elif action == "list_week":
                result = calendar_tools.list_week_events()
                return result.get("message", "No events this week.")
            
            elif action == "check_specific_time":
                result = calendar_tools.check_specific_time(
                    time_min=calendar_action.get("time_min"),
                    time_max=calendar_action.get("time_max"),
                )
                return result.get("message", "Could not check time.")

        if category == "calendar_need_more_info" and calendar_action:
            date = calendar_action.get("date")
            if date:
                if context:
                    update_conversation_context(
                        context.phone_number,
                        last_action="awaiting_event_title",
                        pending_confirmation=date,
                        last_event_details={"title": None, "date": date}
                    )
                return f"Got it. What should I call this all-day event on {date}?"

        # Task commands
            title = msg.replace("add ", "").replace(" to my tasks", "").strip()
            result = execute_tool("save_task", title=title)
            return "Added to tasks."

        if msg.startswith("note: ") or msg.startswith("save this idea: "):
            content = msg.replace("note: ", "").replace("save this idea: ", "").strip()
            result = execute_tool("save_note", content=content)
            return "Saved."

        if "what are my tasks today" in msg or "today's tasks" in msg:
            result = execute_tool("get_today_tasks")
            return format_task_response(result.get("tasks", []))

        if "show all tasks" in msg:
            result = execute_tool("get_all_tasks")
            return format_task_response(result.get("tasks", []))

        if "delete task" in msg:
            match = re.search(r"delete task (\d+)", msg)
            if match:
                task_id = int(match.group(1))
                result = execute_tool("delete_task", task_id=task_id)
                return result.get("message", "Task deleted.")

        if "complete task" in msg:
            match = re.search(r"complete task (\d+)", msg)
            if match:
                task_id = int(match.group(1))
                result = execute_tool("complete_task", task_id=task_id)
                return result.get("message", "Task completed!")

        if "show all notes" in msg:
            result = execute_tool("get_all_notes")
            return format_note_response(result.get("notes", []))

        if "delete note" in msg:
            match = re.search(r"delete note (\d+)", msg)
            if match:
                note_id = int(match.group(1))
                result = execute_tool("delete_note", note_id=note_id)
                return result.get("message", "Note deleted.")

        if "what ideas do i have about" in msg or "search my notes for" in msg:
            query = msg.replace("what ideas do i have about ", "").replace("search my notes for ", "").strip()
            query = query.rstrip("?")
            result = execute_tool("search_notes", query=query)
            return format_note_response(result.get("notes", []))

        if msg.startswith("remind me to "):
            match = re.search(r"remind me to (.+) at (.+)", msg)
            if match:
                title = match.group(1).strip()
                due_time = match.group(2).strip()
                result = execute_tool("save_task", title=title, due_time=due_time)
                return "Added to tasks with reminder."

        if "delete all tasks" in msg:
            result = execute_tool("delete_all_tasks")
            return result.get("message", "All tasks deleted.")

        if "delete all notes" in msg:
            result = execute_tool("delete_all_notes")
            return result.get("message", "All notes deleted.")

        return "I understand. Try commands like:\n• Add [task] to my tasks\n• Note: [idea]\n• What are my tasks today?\n• Show all tasks\n• Show all notes"


agent = Agent()
