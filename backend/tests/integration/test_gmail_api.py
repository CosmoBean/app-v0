"""
Integration tests for Gmail API
"""
import pytest
from unittest.mock import patch, Mock


@pytest.mark.integration
class TestGmailAPI:
    """Test Gmail API endpoints"""

    def test_get_messages_unauthorized(self, client):
        """Test messages endpoint without auth"""
        response = client.post("/gmail/messages", json={})
        assert response.status_code == 422  # Missing authorization header

    def test_get_messages_authorized(self, client, sample_email):
        """Test fetching messages with auth"""
        with patch("app.routers.gmail.GmailService") as mock_service:
            mock_instance = Mock()
            mock_instance.get_messages.return_value = {
                "messages": [sample_email],
                "total": 1,
            }
            mock_service.return_value = mock_instance

            response = client.post(
                "/gmail/messages",
                json={"max_results": 10},
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "messages" in data
            assert "total" in data

    def test_get_single_message(self, client, sample_email):
        """Test getting single message"""
        with patch("app.routers.gmail.GmailService") as mock_service:
            mock_instance = Mock()
            mock_instance.get_message.return_value = sample_email
            mock_service.return_value = mock_instance

            response = client.get(
                "/gmail/messages/email123",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "email123"

    def test_summarize_email(self, client):
        """Test email summarization endpoint"""
        with patch("app.routers.gmail.GmailService") as mock_gmail:
            with patch("app.routers.gmail.AIService") as mock_ai:
                mock_gmail_instance = Mock()
                mock_gmail_instance.get_message.return_value = {
                    "id": "email123",
                    "subject": "Test",
                    "body_text": "Test body"
                }
                mock_gmail.return_value = mock_gmail_instance

                mock_ai_instance = Mock()
                mock_ai_instance.summarize_email.return_value = "Test summary"
                mock_ai.return_value = mock_ai_instance

                response = client.post(
                    "/gmail/messages/email123/summarize",
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert "summary" in data

    def test_archive_message(self, client):
        """Test archiving message"""
        with patch("app.routers.gmail.GmailService") as mock_service:
            mock_instance = Mock()
            mock_instance.archive_message.return_value = {"id": "email123"}
            mock_service.return_value = mock_instance

            response = client.post(
                "/gmail/messages/email123/archive",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "archived"

    def test_trash_message(self, client):
        """Test trashing message"""
        with patch("app.routers.gmail.GmailService") as mock_service:
            mock_instance = Mock()
            mock_instance.trash_message.return_value = {"id": "email123"}
            mock_service.return_value = mock_instance

            response = client.post(
                "/gmail/messages/email123/trash",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "trashed"

    def test_process_batch(self, client, sample_email):
        """Test batch processing endpoint"""
        with patch("app.routers.gmail.EmailOrganizer") as mock_organizer:
            with patch("app.routers.gmail.GmailService") as mock_gmail:
                with patch("app.routers.gmail.AIService"):
                    mock_gmail_instance = Mock()
                    mock_gmail_instance.get_messages.return_value = {
                        "messages": [sample_email]
                    }
                    mock_gmail.return_value = mock_gmail_instance

                    mock_org_instance = Mock()
                    mock_org_instance.auto_categorize_and_label.return_value = sample_email
                    mock_organizer.return_value = mock_org_instance

                    response = client.post(
                        "/gmail/process-batch",
                        json={
                            "query": "is:unread",
                            "max_results": 10,
                            "auto_categorize": True
                        },
                        headers={"Authorization": "Bearer test_token"}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "total" in data
                    assert "emails" in data

    def test_get_labels(self, client):
        """Test getting labels"""
        with patch("app.routers.gmail.GmailService") as mock_service:
            mock_instance = Mock()
            mock_instance.get_labels.return_value = [
                {"id": "INBOX", "name": "INBOX"},
                {"id": "SENT", "name": "SENT"},
            ]
            mock_service.return_value = mock_instance

            response = client.get(
                "/gmail/labels",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "labels" in data
