"""
Calendar event models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base


class CalendarEvent(Base):
    """Calendar event model"""

    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Google Calendar metadata
    google_event_id = Column(String(255), unique=True, index=True)
    calendar_id = Column(String(255), default="primary")

    # Event details
    title = Column(String(500))
    description = Column(Text)
    location = Column(String(500))

    # Time
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    timezone = Column(String(100))
    is_all_day = Column(Boolean, default=False)

    # Attendees
    attendees = Column(Text)  # JSON array as text
    organizer = Column(String(255))

    # AI-generated content
    summary = Column(Text)
    ai_tags = Column(Text)  # JSON array as text
    related_email_id = Column(Integer, ForeignKey("emails.id"))  # If created from email

    # Status
    status = Column(String(50))  # confirmed, tentative, cancelled
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="calendar_events")

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title={self.title})>"
