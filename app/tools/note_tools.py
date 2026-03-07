"""Note tools for the AI agent."""
from typing import Dict, Any, Optional

from app.services.note_service import note_service
from app.services.search_service import search_service


def save_note(content: str, tags: Optional[str] = None) -> Dict[str, Any]:
    """Save a new note."""
    try:
        note = note_service.create_note(content=content, tags=tags)
        return {
            "success": True,
            "message": "Note saved",
            "note": note,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to save note: {str(e)}",
        }


def search_notes(query: str) -> Dict[str, Any]:
    """Search notes by query."""
    try:
        notes = search_service.search_notes(query)
        return {
            "success": True,
            "notes": notes,
            "count": len(notes),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to search notes: {str(e)}",
        }


def get_recent_notes(limit: int = 5) -> Dict[str, Any]:
    """Get recent notes."""
    try:
        notes = note_service.get_recent_notes(limit=limit)
        return {
            "success": True,
            "notes": notes,
            "count": len(notes),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get notes: {str(e)}",
        }


def get_all_notes(limit: int = 50) -> Dict[str, Any]:
    """Get all notes."""
    try:
        notes = note_service.get_all_notes(limit=limit)
        return {
            "success": True,
            "notes": notes,
            "count": len(notes),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get notes: {str(e)}",
        }
