"""
User settings and API usage tracking models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base


class UserSettings(Base):
    """User settings and preferences"""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # AI Provider Settings
    ai_provider = Column(String(50), default="anthropic")  # anthropic, openai, local
    use_project_keys = Column(Boolean, default=True)  # Use free tier or BYOK

    # BYOK (Bring Your Own Keys)
    anthropic_api_key = Column(Text)  # Encrypted
    openai_api_key = Column(Text)  # Encrypted
    local_ai_endpoint = Column(String(500))

    # Model Preferences
    anthropic_model = Column(String(100), default="claude-3-5-sonnet-20241022")
    openai_model = Column(String(100), default="gpt-4-turbo-preview")
    local_model = Column(String(100), default="llama2")

    # Email Organization Preferences
    auto_categorize = Column(Boolean, default=True)
    auto_tag = Column(Boolean, default=True)
    auto_summarize = Column(Boolean, default=True)
    auto_archive_newsletters = Column(Boolean, default=False)
    auto_archive_promotions = Column(Boolean, default=False)

    # Calendar Preferences
    auto_create_events = Column(Boolean, default=False)
    calendar_lookahead_days = Column(Integer, default=30)
    default_event_duration = Column(Integer, default=60)  # minutes

    # Notification Preferences
    enable_notifications = Column(Boolean, default=True)
    notification_email = Column(String(255))

    # Custom Categories (JSON)
    custom_categories = Column(Text)  # JSON array
    custom_rules = Column(Text)  # JSON array of custom organization rules

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, ai_provider={self.ai_provider})>"


class APIKeyUsage(Base):
    """Track API key usage for free tier limits"""

    __tablename__ = "api_key_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Usage tracking
    year_month = Column(String(7), index=True)  # Format: YYYY-MM
    provider = Column(String(50))  # anthropic, openai
    request_count = Column(Integer, default=0)
    token_count = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)  # In USD

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_usage")

    def __repr__(self):
        return f"<APIKeyUsage(user_id={self.user_id}, month={self.year_month}, requests={self.request_count})>"
