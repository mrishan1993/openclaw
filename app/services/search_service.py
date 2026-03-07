"""Search service for notes."""
from typing import List
from sqlalchemy.orm import Session

from app.database.models import Note
from app.database.db import get_db_session


class SearchService:
    """Service for searching notes."""

    def search_notes(self, query: str, limit: int = 10) -> List[dict]:
        """Search notes by content or tags using keyword matching."""
        with get_db_session() as session:
            search_pattern = f"%{query}%"
            notes = (
                session.query(Note)
                .filter(
                    (Note.content.like(search_pattern)) | (Note.tags.like(search_pattern))
                )
                .order_by(Note.created_at.desc())
                .limit(limit)
                .all()
            )
            return [note.to_dict() for note in notes]

    def search_by_tags(self, tags: str, limit: int = 10) -> List[dict]:
        """Search notes by tags."""
        with get_db_session() as session:
            tag_list = [t.strip().lower() for t in tags.split(",")]
            notes = session.query(Note).all()
            results = []
            for note in notes:
                if note.tags:
                    note_tags = [t.strip().lower() for t in note.tags.split(",")]
                    if any(tag in note_tags for tag in tag_list):
                        results.append(note.to_dict())
            return results[:limit]


search_service = SearchService()
