"""
Pytest configuration and fixtures
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from google.oauth2.credentials import Credentials
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.services import GmailService, CalendarService, AIService, EmailOrganizer


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_credentials():
    """Mock Google OAuth credentials"""
    return Credentials(
        token="mock_access_token",
        refresh_token="mock_refresh_token",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="mock_client_id",
        client_secret="mock_client_secret",
    )


@pytest.fixture
def mock_gmail_service(mock_credentials):
    """Mock Gmail service"""
    return GmailService(mock_credentials)


@pytest.fixture
def mock_calendar_service(mock_credentials):
    """Mock Calendar service"""
    return CalendarService(mock_credentials)


@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    return AIService(provider="anthropic", api_key="mock_key", use_project_keys=False)


@pytest.fixture
def sample_email():
    """Sample email data"""
    return {
        "id": "email123",
        "thread_id": "thread123",
        "subject": "Test Email Subject",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "snippet": "This is a test email snippet",
        "body_text": "This is the full body of the test email with important information.",
        "body_html": "<p>This is the full body of the test email</p>",
        "date": "Mon, 1 Jan 2024 10:00:00 -0800",
        "labels": ["INBOX", "UNREAD"],
        "internal_date": "2024-01-01T10:00:00",
    }


@pytest.fixture
def sample_calendar_event():
    """Sample calendar event data"""
    return {
        "id": "event123",
        "summary": "Team Meeting",
        "description": "Weekly team sync",
        "start": {
            "dateTime": "2024-01-15T14:00:00-08:00",
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": "2024-01-15T15:00:00-08:00",
            "timeZone": "America/Los_Angeles",
        },
        "location": "Conference Room A",
        "attendees": [{"email": "colleague@example.com"}],
    }


@pytest.fixture
def sample_chat_messages():
    """Sample chat messages"""
    return [
        {"role": "user", "content": "Summarize my unread emails"},
    ]


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response"""
    mock_response = Mock()
    mock_response.content = [Mock(text="This is a mock AI response")]
    return mock_response


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="This is a mock AI response"))]
    return mock_response
