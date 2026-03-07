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

    def _build_messages(self, user_message: str) -> list:
        """Build message list for OpenClaw API."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

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

    def process_message(self, user_message: str) -> str:
        """Process user message and return response."""
        logger.info(f"Processing message: {user_message}")

        messages = self._build_messages(user_message)
        response = self._call_openclaw(messages)

        if not response:
            return self._fallback_response(user_message)

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
            else:
                responses.append("Done.")

        return " ".join(responses)

    def _fallback_response(self, message: str) -> str:
        """Simple rule-based fallback when OpenClaw API is unavailable."""
        import re

        msg = message.lower().strip()

        if msg.startswith("add ") and " to my tasks" in msg:
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

        return "I understand. Try commands like:\n• Add [task] to my tasks\n• Note: [idea]\n• What are my tasks today?\n• Show all tasks\n• Show all notes"


agent = Agent()
