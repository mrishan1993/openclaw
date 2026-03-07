"""Note service for managing notes."""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.models import Note
from app.database.db import get_db_session


class NoteService:
    """Service for note operations."""

    def create_note(self, content: str, tags: Optional[str] = None) -> dict:
        """Create a new note."""
        with get_db_session() as session:
            note = Note(content=content, tags=tags)
            session.add(note)
            session.flush()
            return note.to_dict()

    def get_all_notes(self, limit: int = 50) -> List[dict]:
        """Get all notes ordered by creation date."""
        with get_db_session() as session:
            notes = (
                session.query(Note)
                .order_by(Note.created_at.desc())
                .limit(limit)
                .all()
            )
            return [note.to_dict() for note in notes]

    def get_recent_notes(self, limit: int = 5) -> List[dict]:
        """Get recent notes."""
        with get_db_session() as session:
            notes = (
                session.query(Note)
                .order_by(Note.created_at.desc())
                .limit(limit)
                .all()
            )
            return [note.to_dict() for note in notes]

    def get_note_by_id(self, note_id: int) -> Optional[dict]:
        """Get a note by ID."""
        with get_db_session() as session:
            note = session.query(Note).filter(Note.id == note_id).first()
            return note.to_dict() if note else None


note_service = NoteService()
