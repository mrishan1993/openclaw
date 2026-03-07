"""Task tools for the AI agent."""
from datetime import datetime
from typing import Optional, Dict, Any

from app.services.task_service import task_service


def save_task(title: str, due_time: Optional[str] = None) -> Dict[str, Any]:
    """Save a new task."""
    try:
        due_dt = None
        if due_time:
            due_dt = datetime.fromisoformat(due_time.replace("Z", "+00:00"))

        task = task_service.create_task(title=title, due_time=due_dt)
        return {
            "success": True,
            "message": "Task saved",
            "task": task,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to save task: {str(e)}",
        }


def get_today_tasks() -> Dict[str, Any]:
    """Get all tasks for today."""
    try:
        tasks = task_service.get_today_tasks()
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get tasks: {str(e)}",
        }


def get_all_tasks() -> Dict[str, Any]:
    """Get all pending tasks."""
    try:
        tasks = task_service.get_all_pending_tasks()
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get tasks: {str(e)}",
        }


def delete_task(task_id: int) -> Dict[str, Any]:
    """Delete a task by ID."""
    try:
        result = task_service.delete_task(task_id)
        return {
            "success": True,
            "message": "Task deleted",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to delete task: {str(e)}",
        }


def complete_task(task_id: int) -> Dict[str, Any]:
    """Mark a task as completed."""
    try:
        result = task_service.complete_task(task_id)
        if result:
            return {
                "success": True,
                "message": "Task completed!",
            }
        return {
            "success": False,
            "message": "Task not found",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to complete task: {str(e)}",
        }


def delete_all_tasks() -> Dict[str, Any]:
    """Delete all tasks."""
    try:
        count = task_service.delete_all_tasks()
        return {
            "success": True,
            "message": f"Deleted {count} tasks",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to delete tasks: {str(e)}",
        }
