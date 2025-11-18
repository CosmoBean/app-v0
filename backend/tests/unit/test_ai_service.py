"""
Tests for AI service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.ai_service import AIService


@pytest.mark.unit
class TestAIService:
    """Test AI service functionality"""

    @pytest.mark.asyncio
    async def test_summarize_email(self, mock_ai_service, mock_anthropic_response):
        """Test email summarization"""
        with patch.object(
            mock_ai_service.client.messages, "create", return_value=mock_anthropic_response
        ):
            summary = await mock_ai_service.summarize_email(
                "This is a long email about a meeting tomorrow at 2pm"
            )
            assert isinstance(summary, str)
            assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_categorize_email(self, mock_ai_service, mock_anthropic_response):
        """Test email categorization"""
        mock_anthropic_response.content[0].text = "newsletter"

        with patch.object(
            mock_ai_service.client.messages, "create", return_value=mock_anthropic_response
        ):
            category = await mock_ai_service.categorize_email(
                "Subscribe to our weekly newsletter!",
                "newsletter@example.com",
                "Weekly Newsletter"
            )
            assert category in [
                "important", "newsletter", "social", "promotions",
                "work", "personal", "spam", "unclassified"
            ]

    @pytest.mark.asyncio
    async def test_extract_tags(self, mock_ai_service, mock_anthropic_response):
        """Test tag extraction from email"""
        mock_anthropic_response.content[0].text = "meeting, project, deadline"

        with patch.object(
            mock_ai_service.client.messages, "create", return_value=mock_anthropic_response
        ):
            tags = await mock_ai_service.extract_tags(
                "Let's discuss the project deadline in tomorrow's meeting",
                "Project Discussion"
            )
            assert isinstance(tags, list)
            assert len(tags) <= 5

    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, mock_ai_service, mock_anthropic_response):
        """Test sentiment analysis"""
        mock_anthropic_response.content[0].text = "positive"

        with patch.object(
            mock_ai_service.client.messages, "create", return_value=mock_anthropic_response
        ):
            sentiment = await mock_ai_service.analyze_sentiment(
                "Great job on the presentation! Really impressed."
            )
            assert sentiment in ["positive", "negative", "neutral"]

    @pytest.mark.asyncio
    async def test_calculate_priority(self, mock_ai_service, mock_anthropic_response):
        """Test priority score calculation"""
        mock_anthropic_response.content[0].text = "85"

        with patch.object(
            mock_ai_service.client.messages, "create", return_value=mock_anthropic_response
        ):
            priority = await mock_ai_service.calculate_priority(
                "URGENT: Server is down!",
                "ops@example.com",
                "URGENT: Production Issue"
            )
            assert isinstance(priority, int)
            assert 0 <= priority <= 100

    @pytest.mark.asyncio
    async def test_chat_completion_anthropic(self, mock_anthropic_response):
        """Test chat completion with Anthropic"""
        ai_service = AIService(provider="anthropic", api_key="test_key", use_project_keys=False)

        with patch.object(
            ai_service.client.messages, "create", return_value=mock_anthropic_response
        ):
            messages = [{"role": "user", "content": "Hello"}]
            response = await ai_service.chat_completion(messages)
            assert isinstance(response, str)
            assert len(response) > 0

    @pytest.mark.asyncio
    async def test_chat_completion_openai(self, mock_openai_response):
        """Test chat completion with OpenAI"""
        ai_service = AIService(provider="openai", api_key="test_key", use_project_keys=False)

        with patch.object(
            ai_service.client.chat.completions, "create", return_value=mock_openai_response
        ):
            messages = [{"role": "user", "content": "Hello"}]
            response = await ai_service.chat_completion(messages)
            assert isinstance(response, str)
            assert len(response) > 0

    @pytest.mark.asyncio
    async def test_extract_event_from_email(self, mock_ai_service, mock_anthropic_response):
        """Test event extraction from email"""
        mock_anthropic_response.content[0].text = '''
        {
            "title": "Team Meeting",
            "date": "2024-01-15",
            "start_time": "14:00",
            "end_time": "15:00",
            "location": "Room 101"
        }
        '''

        with patch.object(
            mock_ai_service.client.messages, "create", return_value=mock_anthropic_response
        ):
            event = await mock_ai_service.extract_event_from_email(
                "Let's meet tomorrow at 2pm in Room 101"
            )
            assert event is not None
            assert "title" in event
            assert "date" in event

    def test_provider_initialization_anthropic(self):
        """Test Anthropic provider initialization"""
        ai_service = AIService(provider="anthropic", api_key="test_key", use_project_keys=False)
        assert ai_service.provider == "anthropic"
        assert ai_service.is_byok is True

    def test_provider_initialization_openai(self):
        """Test OpenAI provider initialization"""
        ai_service = AIService(provider="openai", api_key="test_key", use_project_keys=False)
        assert ai_service.provider == "openai"
        assert ai_service.is_byok is True

    def test_invalid_provider_raises_error(self):
        """Test invalid provider raises error"""
        with pytest.raises(ValueError):
            AIService(provider="invalid_provider", api_key="test_key", use_project_keys=False)
