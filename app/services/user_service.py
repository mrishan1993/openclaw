"""User service for managing user data and Google Calendar tokens."""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_or_create_user(phone_number: str) -> User:
    """Get or create a user by phone number."""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {phone_number}")
        return user
    finally:
        db.close()


def update_user_google_tokens(
    phone_number: str,
    access_token: str,
    refresh_token: Optional[str] = None,
    token_expiry: Optional[datetime] = None
) -> User:
    """Update user's Google tokens."""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.add(user)
        
        user.google_access_token = access_token
        if refresh_token:
            user.google_refresh_token = refresh_token
        if token_expiry:
            user.google_token_expiry = token_expiry
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        logger.info(f"Updated Google tokens for user: {phone_number}")
        return user
    finally:
        db.close()


def get_user_google_token(phone_number: str) -> Optional[str]:
    """Get user's Google access token."""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if user and user.google_access_token:
            if user.google_token_expiry and user.google_token_expiry < datetime.utcnow():
                logger.info(f"Token expired for user: {phone_number}, need refresh")
                return None
            return user.google_access_token
        return None
    finally:
        db.close()


def has_google_access(phone_number: str) -> bool:
    """Check if user has Google Calendar access configured."""
    token = get_user_google_token(phone_number)
    return token is not None


def delete_user_google_tokens(phone_number: str) -> bool:
    """Remove Google tokens from user (disconnect)."""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if user:
            user.google_access_token = None
            user.google_refresh_token = None
            user.google_token_expiry = None
            user.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Removed Google tokens for user: {phone_number}")
            return True
        return False
    finally:
        db.close()
