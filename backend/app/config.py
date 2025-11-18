"""
Configuration management for Gmail AI Organizer
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Gmail AI Organizer"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./gmail_organizer.db"

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    GOOGLE_SCOPES: str = "https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/calendar"

    @property
    def google_scopes_list(self) -> List[str]:
        """Convert comma-separated scopes to list"""
        return [scope.strip() for scope in self.GOOGLE_SCOPES.split(",")]

    # AI Configuration - BYOK
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Project Keys (Free Tier)
    PROJECT_ANTHROPIC_KEY: str = ""
    PROJECT_OPENAI_KEY: str = ""
    FREE_TIER_MONTHLY_LIMIT: int = 100

    # AI Models
    DEFAULT_AI_PROVIDER: str = "anthropic"  # anthropic, openai, local
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Local AI
    LOCAL_AI_ENABLED: bool = False
    LOCAL_AI_ENDPOINT: str = "http://localhost:11434"
    LOCAL_AI_MODEL: str = "llama2"

    # Email Processing
    MAX_EMAILS_PER_REQUEST: int = 50
    EMAIL_BATCH_SIZE: int = 10
    AUTO_CATEGORIZE: bool = True

    # Calendar
    CALENDAR_LOOKAHEAD_DAYS: int = 30
    AUTO_CREATE_EVENTS: bool = False

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Session
    SESSION_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Feature Flags
    ENABLE_ANALYTICS: bool = True
    ENABLE_EMAIL_SUMMARIZATION: bool = True
    ENABLE_AUTO_TAGGING: bool = True
    ENABLE_SMART_REPLIES: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Uses lru_cache to ensure settings are only loaded once
    """
    return Settings()


# Convenience function for direct import
settings = get_settings()
