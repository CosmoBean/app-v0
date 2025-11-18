"""
Tests for Email Organizer
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.organizer import EmailOrganizer


@pytest.mark.unit
class TestEmailOrganizer:
    """Test Email Organizer functionality"""

    @pytest.mark.asyncio
    async def test_process_email(
        self, mock_gmail_service, mock_ai_service, sample_email
    ):
        """Test processing single email with AI"""
        organizer = EmailOrganizer(mock_gmail_service, mock_ai_service)

        with patch.object(mock_ai_service, "summarize_email", return_value="Test summary"):
            with patch.object(mock_ai_service, "categorize_email", return_value="work"):
                with patch.object(mock_ai_service, "extract_tags", return_value=["meeting", "project"]):
                    with patch.object(mock_ai_service, "analyze_sentiment", return_value="neutral"):
                        with patch.object(mock_ai_service, "calculate_priority", return_value=75):
                            result = await organizer.process_email(sample_email)

                            assert result["summary"] == "Test summary"
                            assert result["category"] == "work"
                            assert "meeting" in result["ai_tags"]
                            assert result["sentiment"] == "neutral"
                            assert result["priority_score"] == 75

    @pytest.mark.asyncio
    async def test_process_batch(
        self, mock_gmail_service, mock_ai_service, sample_email
    ):
        """Test processing batch of emails"""
        organizer = EmailOrganizer(mock_gmail_service, mock_ai_service)
        emails = [sample_email.copy() for _ in range(5)]

        with patch.object(organizer, "process_email", return_value=sample_email):
            results = await organizer.process_batch(emails, batch_size=2)
            assert len(results) == 5

    @pytest.mark.asyncio
    async def test_auto_categorize_and_label(
        self, mock_gmail_service, mock_ai_service, sample_email
    ):
        """Test auto categorization with label application"""
        organizer = EmailOrganizer(mock_gmail_service, mock_ai_service)

        with patch.object(organizer, "process_email") as mock_process:
            mock_process.return_value = {
                **sample_email,
                "category": "newsletter",
            }

            with patch.object(mock_gmail_service, "modify_message") as mock_modify:
                result = await organizer.auto_categorize_and_label(
                    sample_email,
                    apply_labels=True
                )

                assert result["category"] == "newsletter"
                mock_modify.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_action_items(
        self, mock_gmail_service, mock_ai_service
    ):
        """Test extracting action items from email"""
        organizer = EmailOrganizer(mock_gmail_service, mock_ai_service)

        mock_response = "- Review the proposal\n- Schedule follow-up meeting\n- Send feedback"

        with patch.object(mock_ai_service, "_generate", return_value=mock_response):
            items = await organizer.extract_action_items(
                "Please review the proposal and schedule a follow-up meeting."
            )

            assert isinstance(items, list)
            assert len(items) > 0

    @pytest.mark.asyncio
    async def test_suggest_reply(
        self, mock_gmail_service, mock_ai_service
    ):
        """Test generating suggested reply"""
        organizer = EmailOrganizer(mock_gmail_service, mock_ai_service)

        mock_response = "Thank you for your email. I'll review and get back to you soon."

        with patch.object(mock_ai_service, "_generate", return_value=mock_response):
            reply = await organizer.suggest_reply(
                "Can you review this document?",
                tone="professional"
            )

            assert isinstance(reply, str)
            assert len(reply) > 0

    @pytest.mark.asyncio
    async def test_find_similar_emails(
        self, mock_gmail_service, mock_ai_service, sample_email
    ):
        """Test finding similar emails"""
        organizer = EmailOrganizer(mock_gmail_service, mock_ai_service)

        reference = {
            **sample_email,
            "category": "work",
            "ai_tags": ["meeting", "project"],
        }

        all_emails = [
            {**sample_email, "id": "1", "category": "work", "ai_tags": ["meeting"]},
            {**sample_email, "id": "2", "category": "personal", "ai_tags": []},
            {**sample_email, "id": "3", "category": "work", "ai_tags": ["project"]},
        ]

        similar = await organizer.find_similar_emails(reference, all_emails, limit=2)

        assert len(similar) <= 2
        # Should prioritize emails with same category and tags

    @pytest.mark.asyncio
    async def test_smart_archive_old_emails(
        self, mock_gmail_service, mock_ai_service, sample_email
    ):
        """Test smart archiving of old emails"""
        organizer = EmailOrganizer(mock_gmail_service, mock_ai_service)

        mock_emails = {
            "messages": [
                {**sample_email, "id": "1"},
                {**sample_email, "id": "2"},
            ]
        }

        with patch.object(mock_gmail_service, "get_messages", return_value=mock_emails):
            with patch.object(organizer, "process_email") as mock_process:
                mock_process.return_value = {**sample_email, "category": "newsletter"}

                with patch.object(mock_gmail_service, "batch_modify") as mock_batch:
                    count = await organizer.smart_archive_old_emails(
                        days_old=30,
                        categories=["newsletter"]
                    )

                    assert count == 2
                    mock_batch.assert_called_once()
