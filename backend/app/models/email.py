"""
Email models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .user import Base


class EmailCategory(str, enum.Enum):
    """Email category enumeration"""

    IMPORTANT = "important"
    NEWSLETTER = "newsletter"
    SOCIAL = "social"
    PROMOTIONS = "promotions"
    WORK = "work"
    PERSONAL = "personal"
    SPAM = "spam"
    UNCLASSIFIED = "unclassified"


class Email(Base):
    """Email model for storing email metadata and AI-generated content"""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Gmail metadata
    gmail_id = Column(String(255), unique=True, index=True, nullable=False)
    thread_id = Column(String(255), index=True)
    subject = Column(Text)
    sender = Column(String(255), index=True)
    recipient = Column(String(255))
    cc = Column(Text)  # Comma-separated
    bcc = Column(Text)  # Comma-separated

    # Content
    snippet = Column(Text)
    body_text = Column(Text)
    body_html = Column(Text)

    # AI-generated content
    summary = Column(Text)
    category = Column(Enum(EmailCategory), default=EmailCategory.UNCLASSIFIED)
    ai_tags = Column(Text)  # JSON array as text
    sentiment = Column(String(50))  # positive, negative, neutral
    priority_score = Column(Integer, default=0)  # 0-100

    # Gmail labels
    labels = Column(Text)  # JSON array as text

    # Flags
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)

    # Timestamps
    received_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)  # When AI processing was done

    # Relationships
    user = relationship("User", back_populates="emails")

    def __repr__(self):
        return f"<Email(id={self.id}, subject={self.subject[:50]})>"
