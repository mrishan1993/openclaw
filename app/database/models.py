"""Database models for tasks and notes."""
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Task(Base):
    """Task model for storing user tasks."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_time = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "completed": self.completed,
        }


class Note(Base):
    """Note model for storing user notes."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    tags = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert note to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
