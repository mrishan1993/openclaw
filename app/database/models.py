"""Database models for tasks and notes."""
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User model for storing user info and Google tokens."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "has_google_token": bool(self.google_access_token),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


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
