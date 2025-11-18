"""
Integration tests for Chat API
"""
import pytest
from unittest.mock import patch, Mock


@pytest.mark.integration
class TestChatAPI:
    """Test Chat API endpoints"""

    def test_chat_message(self, client, sample_chat_messages):
        """Test chat message endpoint"""
        with patch("app.routers.chat.chatAPI.sendMessage") as mock_send:
            with patch("app.routers.chat.AIService") as mock_ai:
                with patch("app.routers.chat.GmailService"):
                    with patch("app.routers.chat.CalendarService"):
                        mock_ai_instance = Mock()
                        mock_ai_instance.chat_completion.return_value = (
                            "You have 5 unread emails..."
                        )
                        mock_ai.return_value = mock_ai_instance

                        response = client.post(
                            "/chat/message",
                            json={
                                "messages": sample_chat_messages,
                                "include_email_context": True
                            },
                            headers={"Authorization": "Bearer test_token"}
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert "message" in data

    def test_quick_action_summarize_unread(self, client, sample_email):
        """Test quick action - summarize unread"""
        with patch("app.routers.chat.GmailService") as mock_gmail:
            with patch("app.routers.chat.AIService") as mock_ai:
                with patch("app.routers.chat.CalendarService"):
                    mock_gmail_instance = Mock()
                    mock_gmail_instance.get_messages.return_value = {
                        "messages": [sample_email]
                    }
                    mock_gmail.return_value = mock_gmail_instance

                    mock_ai_instance = Mock()
                    mock_ai_instance.summarize_email.return_value = "Test summary"
                    mock_ai.return_value = mock_ai_instance

                    response = client.post(
                        "/chat/quick-action",
                        json={"action": "summarize_unread"},
                        headers={"Authorization": "Bearer test_token"}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["action"] == "summarize_unread"

    def test_quick_action_show_today_schedule(self, client, sample_calendar_event):
        """Test quick action - show today's schedule"""
        with patch("app.routers.chat.CalendarService") as mock_calendar:
            with patch("app.routers.chat.GmailService"):
                with patch("app.routers.chat.AIService"):
                    mock_calendar_instance = Mock()
                    mock_calendar_instance.get_events.return_value = [sample_calendar_event]
                    mock_calendar.return_value = mock_calendar_instance

                    response = client.post(
                        "/chat/quick-action",
                        json={"action": "show_today_schedule"},
                        headers={"Authorization": "Bearer test_token"}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["action"] == "show_today_schedule"
                    assert "events" in data

    def test_quick_action_archive_newsletters(self, client):
        """Test quick action - archive newsletters"""
        with patch("app.routers.chat.EmailOrganizer") as mock_organizer:
            with patch("app.routers.chat.GmailService"):
                with patch("app.routers.chat.CalendarService"):
                    with patch("app.routers.chat.AIService"):
                        mock_org_instance = Mock()
                        mock_org_instance.smart_archive_old_emails.return_value = 10
                        mock_organizer.return_value = mock_org_instance

                        response = client.post(
                            "/chat/quick-action",
                            json={"action": "archive_newsletters"},
                            headers={"Authorization": "Bearer test_token"}
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert data["archived_count"] == 10

    def test_get_suggestions(self, client, sample_email):
        """Test getting AI suggestions"""
        with patch("app.routers.chat.GmailService") as mock_gmail:
            with patch("app.routers.chat.AIService") as mock_ai:
                with patch("app.routers.chat.EmailOrganizer") as mock_organizer:
                    mock_gmail_instance = Mock()
                    mock_gmail_instance.get_messages.return_value = {
                        "messages": [sample_email] * 10
                    }
                    mock_gmail.return_value = mock_gmail_instance

                    mock_org_instance = Mock()
                    processed_email = {**sample_email, "category": "newsletter"}
                    mock_org_instance.process_email.return_value = processed_email
                    mock_organizer.return_value = mock_org_instance

                    response = client.get(
                        "/chat/suggestions",
                        headers={"Authorization": "Bearer test_token"}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "suggestions" in data
                    assert "email_stats" in data

    def test_quick_action_invalid(self, client):
        """Test invalid quick action"""
        with patch("app.routers.chat.GmailService"):
            with patch("app.routers.chat.CalendarService"):
                with patch("app.routers.chat.AIService"):
                    response = client.post(
                        "/chat/quick-action",
                        json={"action": "invalid_action"},
                        headers={"Authorization": "Bearer test_token"}
                    )

                    assert response.status_code == 400
