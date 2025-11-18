"""
Tests for Gmail service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.gmail_service import GmailService


@pytest.mark.unit
class TestGmailService:
    """Test Gmail service functionality"""

    @pytest.mark.asyncio
    async def test_get_messages(self, mock_gmail_service, sample_email):
        """Test fetching messages from Gmail"""
        mock_response = {
            "messages": [{"id": "email123", "threadId": "thread123"}],
            "nextPageToken": None,
        }

        with patch.object(
            mock_gmail_service.service.users().messages(),
            "list",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            with patch.object(mock_gmail_service, "get_message", return_value=sample_email):
                result = await mock_gmail_service.get_messages(max_results=10)

                assert "messages" in result
                assert "total" in result
                assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_get_message(self, mock_gmail_service):
        """Test getting single message details"""
        mock_message = {
            "id": "email123",
            "threadId": "thread123",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "test@example.com"},
                ],
                "body": {"data": "VGVzdCBib2R5"},
            },
            "snippet": "Test snippet",
            "labelIds": ["INBOX"],
            "internalDate": "1704106800000",
        }

        with patch.object(
            mock_gmail_service.service.users().messages(),
            "get",
            return_value=Mock(execute=Mock(return_value=mock_message))
        ):
            result = await mock_gmail_service.get_message("email123")

            assert result["id"] == "email123"
            assert "subject" in result
            assert "from" in result

    @pytest.mark.asyncio
    async def test_modify_message(self, mock_gmail_service):
        """Test modifying message labels"""
        mock_response = {"id": "email123", "labelIds": ["INBOX", "IMPORTANT"]}

        with patch.object(
            mock_gmail_service.service.users().messages(),
            "modify",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_gmail_service.modify_message(
                "email123",
                add_labels=["IMPORTANT"]
            )

            assert result["id"] == "email123"

    @pytest.mark.asyncio
    async def test_mark_as_read(self, mock_gmail_service):
        """Test marking message as read"""
        with patch.object(mock_gmail_service, "modify_message") as mock_modify:
            await mock_gmail_service.mark_as_read("email123")
            mock_modify.assert_called_once_with("email123", remove_labels=["UNREAD"])

    @pytest.mark.asyncio
    async def test_mark_as_unread(self, mock_gmail_service):
        """Test marking message as unread"""
        with patch.object(mock_gmail_service, "modify_message") as mock_modify:
            await mock_gmail_service.mark_as_unread("email123")
            mock_modify.assert_called_once_with("email123", add_labels=["UNREAD"])

    @pytest.mark.asyncio
    async def test_star_message(self, mock_gmail_service):
        """Test starring a message"""
        with patch.object(mock_gmail_service, "modify_message") as mock_modify:
            await mock_gmail_service.star_message("email123")
            mock_modify.assert_called_once_with("email123", add_labels=["STARRED"])

    @pytest.mark.asyncio
    async def test_archive_message(self, mock_gmail_service):
        """Test archiving a message"""
        with patch.object(mock_gmail_service, "modify_message") as mock_modify:
            await mock_gmail_service.archive_message("email123")
            mock_modify.assert_called_once_with("email123", remove_labels=["INBOX"])

    @pytest.mark.asyncio
    async def test_trash_message(self, mock_gmail_service):
        """Test moving message to trash"""
        mock_response = {"id": "email123"}

        with patch.object(
            mock_gmail_service.service.users().messages(),
            "trash",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_gmail_service.trash_message("email123")
            assert result["id"] == "email123"

    @pytest.mark.asyncio
    async def test_send_message(self, mock_gmail_service):
        """Test sending an email"""
        mock_response = {"id": "sent123", "labelIds": ["SENT"]}

        with patch.object(
            mock_gmail_service.service.users().messages(),
            "send",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_gmail_service.send_message(
                to="recipient@example.com",
                subject="Test",
                body="Test body"
            )
            assert result["id"] == "sent123"

    @pytest.mark.asyncio
    async def test_get_labels(self, mock_gmail_service):
        """Test getting all labels"""
        mock_labels = {
            "labels": [
                {"id": "INBOX", "name": "INBOX"},
                {"id": "SPAM", "name": "SPAM"},
            ]
        }

        with patch.object(
            mock_gmail_service.service.users().labels(),
            "list",
            return_value=Mock(execute=Mock(return_value=mock_labels))
        ):
            result = await mock_gmail_service.get_labels()
            assert len(result) == 2

    def test_decode_body(self):
        """Test base64 body decoding"""
        encoded = "SGVsbG8gV29ybGQ="  # "Hello World" in base64
        decoded = GmailService._decode_body(encoded)
        assert decoded == "Hello World"

    def test_decode_body_empty(self):
        """Test decoding empty body"""
        decoded = GmailService._decode_body("")
        assert decoded == ""
