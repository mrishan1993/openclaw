"""Task service for managing tasks."""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.models import Task
from app.database.db import get_db_session


class TaskService:
    """Service for task operations."""

    def create_task(
        self, title: str, due_time: Optional[datetime] = None
    ) -> dict:
        """Create a new task."""
        with get_db_session() as session:
            task = Task(title=title, due_time=due_time)
            session.add(task)
            session.flush()
            return task.to_dict()

    def get_today_tasks(self) -> List[dict]:
        """Get all tasks for today."""
        today = date.today()
        with get_db_session() as session:
            tasks = (
                session.query(Task)
                .filter(
                    Task.completed == False,
                    (Task.due_time == None)
                    | (
                        Task.due_time >= datetime.combine(today, datetime.min.time())
                    )
                    & (Task.due_time < datetime.combine(today, datetime.max.time()))
                    | (Task.created_at >= datetime.combine(today, datetime.min.time()))
                    & (Task.created_at < datetime.combine(today, datetime.max.time())),
                )
                .order_by(Task.created_at.desc())
                .all()
            )
            return [task.to_dict() for task in tasks]

    def get_all_pending_tasks(self) -> List[dict]:
        """Get all pending tasks."""
        with get_db_session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.completed == False)
                .order_by(Task.created_at.desc())
                .all()
            )
            return [task.to_dict() for task in tasks]

    def complete_task(self, task_id: int) -> Optional[dict]:
        """Mark a task as completed."""
        with get_db_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.completed = True
                session.flush()
                return task.to_dict()
            return None

    def get_task_by_id(self, task_id: int) -> Optional[dict]:
        """Get a task by ID."""
        with get_db_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            return task.to_dict() if task else None

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        with get_db_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                session.delete(task)
                session.flush()
                return True
            return False

    def delete_all_tasks(self) -> int:
        """Delete all tasks."""
        with get_db_session() as session:
            count = session.query(Task).delete()
            session.flush()
            return count


task_service = TaskService()
