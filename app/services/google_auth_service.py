"""Google OAuth service for calendar authentication."""
from typing import Optional, Dict, Any
import httpx
from datetime import datetime, timedelta

from app.config import get_settings
from app.utils.logger import get_logger
from app.services import user_service

logger = get_logger(__name__)
settings = get_settings()


GOOGLE_OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]


def get_authorization_url(phone_number: str, redirect_uri: str) -> str:
    """Generate Google OAuth authorization URL."""
    import urllib.parse
    
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": phone_number,
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{GOOGLE_OAUTH_URL}?{query_string}"


def exchange_code_for_tokens(code: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access and refresh tokens."""
    data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(GOOGLE_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error exchanging OAuth code: {e}")
        return None


def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Refresh an expired access token."""
    data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(GOOGLE_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return None


def handle_oauth_callback(code: str, phone_number: str) -> Dict[str, Any]:
    """Handle OAuth callback and store tokens for user."""
    token_data = exchange_code_for_tokens(code)
    
    if not token_data:
        return {"success": False, "message": "Failed to obtain access token"}
    
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    
    token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
    
    user_service.update_user_google_tokens(
        phone_number=phone_number,
        access_token=access_token,
        refresh_token=refresh_token,
        token_expiry=token_expiry
    )
    
    logger.info(f"Google Calendar connected for user: {phone_number}")
    return {"success": True, "message": "Google Calendar connected successfully!"}


def disconnect_calendar(phone_number: str) -> Dict[str, Any]:
    """Disconnect user's Google Calendar."""
    success = user_service.delete_user_google_tokens(phone_number)
    if success:
        return {"success": True, "message": "Google Calendar disconnected."}
    return {"success": False, "message": "No calendar connection found."}
