"""Configuration module for loading environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openclaw_api_key: str = ""
    whatsapp_token: str = ""
    whatsapp_phone_id: str = ""
    verify_token: str = ""
    authorized_user: str = ""
    database_url: str = "sqlite:///./whatsapp_assistant.db"
    digest_time: str = "08:00"
    log_level: str = "INFO"
    
    # Google Calendar
    google_access_token: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
