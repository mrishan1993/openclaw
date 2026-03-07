"""Tools registry for the AI agent."""
from typing import Dict, Any, Callable, List
from app.tools import task_tools, note_tools


TOOLS_REGISTRY: Dict[str, Callable] = {
    "save_task": task_tools.save_task,
    "get_today_tasks": task_tools.get_today_tasks,
    "get_all_tasks": task_tools.get_all_tasks,
    "delete_task": task_tools.delete_task,
    "complete_task": task_tools.complete_task,
    "save_note": note_tools.save_note,
    "search_notes": note_tools.search_notes,
    "get_recent_notes": note_tools.get_recent_notes,
    "get_all_notes": note_tools.get_all_notes,
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
}


def get_tool(name: str) -> Callable:
    """Get a tool by name."""
    return TOOLS_REGISTRY.get(name)


def get_all_tools() -> List[Dict[str, Any]]:
    """Get all available tools."""
    return list(TOOL_DESCRIPTIONS.values())


def execute_tool(name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool by name with given arguments."""
    tool = get_tool(name)
    if not tool:
        return {"success": False, "message": f"Tool '{name}' not found"}
    try:
        return tool(**kwargs)
    except Exception as e:
        return {"success": False, "message": str(e)}
