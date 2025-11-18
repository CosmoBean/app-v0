"""
AI service with BYOK (Bring Your Own Keys) support
Supports Anthropic Claude, OpenAI, and local models
"""
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from openai import OpenAI
import httpx
import logging
from datetime import datetime
from ..config import settings

logger = logging.getLogger(__name__)


class AIService:
    """
    AI service supporting multiple providers with BYOK
    """

    def __init__(
        self,
        provider: str = "anthropic",
        api_key: Optional[str] = None,
        use_project_keys: bool = True,
    ):
        """
        Initialize AI service

        Args:
            provider: AI provider (anthropic, openai, local)
            api_key: User's API key (BYOK) or None to use project keys
            use_project_keys: Use free tier project keys if no BYOK
        """
        self.provider = provider.lower()
        self.use_project_keys = use_project_keys

        # Determine which API key to use
        if api_key:
            self.api_key = api_key
            self.is_byok = True
        elif use_project_keys:
            self.api_key = self._get_project_key()
            self.is_byok = False
        else:
            raise ValueError("No API key provided and project keys disabled")

        # Initialize appropriate client
        self._init_client()

    def _get_project_key(self) -> str:
        """Get project API key for free tier"""
        if self.provider == "anthropic":
            return settings.PROJECT_ANTHROPIC_KEY
        elif self.provider == "openai":
            return settings.PROJECT_OPENAI_KEY
        else:
            return ""

    def _init_client(self):
        """Initialize AI client based on provider"""
        if self.provider == "anthropic":
            self.client = Anthropic(api_key=self.api_key)
            self.model = settings.ANTHROPIC_MODEL
        elif self.provider == "openai":
            self.client = OpenAI(api_key=self.api_key)
            self.model = settings.OPENAI_MODEL
        elif self.provider == "local":
            # Local AI support (Ollama, LM Studio, etc.)
            self.endpoint = settings.LOCAL_AI_ENDPOINT
            self.model = settings.LOCAL_AI_MODEL
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    async def summarize_email(self, email_content: str, max_length: int = 200) -> str:
        """
        Summarize email content

        Args:
            email_content: Full email text
            max_length: Maximum summary length

        Returns:
            Email summary
        """
        prompt = f"""Summarize the following email in {max_length} characters or less.
Focus on the main points, action items, and key information.

Email:
{email_content}

Summary:"""

        try:
            response = await self._generate(prompt, max_tokens=150)
            return response.strip()
        except Exception as e:
            logger.error(f"Error summarizing email: {e}")
            return "Error generating summary"

    async def categorize_email(self, email_content: str, sender: str, subject: str) -> str:
        """
        Categorize email into predefined categories

        Args:
            email_content: Email body
            sender: Sender email
            subject: Email subject

        Returns:
            Category (important, newsletter, social, promotions, work, personal, spam, unclassified)
        """
        prompt = f"""Categorize the following email into ONE of these categories:
- important: Urgent or high-priority emails requiring action
- newsletter: Marketing emails, newsletters, subscriptions
- social: Social media notifications
- promotions: Promotional offers, deals, shopping
- work: Work-related emails
- personal: Personal correspondence
- spam: Likely spam or unwanted
- unclassified: Cannot determine

From: {sender}
Subject: {subject}
Body: {email_content[:500]}

Respond with ONLY the category name, nothing else."""

        try:
            response = await self._generate(prompt, max_tokens=20)
            category = response.strip().lower()

            # Validate category
            valid_categories = [
                "important",
                "newsletter",
                "social",
                "promotions",
                "work",
                "personal",
                "spam",
                "unclassified",
            ]
            if category not in valid_categories:
                return "unclassified"

            return category
        except Exception as e:
            logger.error(f"Error categorizing email: {e}")
            return "unclassified"

    async def extract_tags(self, email_content: str, subject: str) -> List[str]:
        """
        Extract relevant tags from email

        Args:
            email_content: Email body
            subject: Email subject

        Returns:
            List of tags
        """
        prompt = f"""Extract 3-5 relevant tags from this email. Tags should be single words or short phrases.
Return tags as a comma-separated list.

Subject: {subject}
Body: {email_content[:500]}

Tags:"""

        try:
            response = await self._generate(prompt, max_tokens=50)
            tags = [tag.strip() for tag in response.split(",")]
            return tags[:5]  # Limit to 5 tags
        except Exception as e:
            logger.error(f"Error extracting tags: {e}")
            return []

    async def analyze_sentiment(self, email_content: str) -> str:
        """
        Analyze email sentiment

        Args:
            email_content: Email text

        Returns:
            Sentiment (positive, negative, neutral)
        """
        prompt = f"""Analyze the sentiment of this email. Respond with ONLY one word: positive, negative, or neutral.

Email: {email_content[:500]}

Sentiment:"""

        try:
            response = await self._generate(prompt, max_tokens=10)
            sentiment = response.strip().lower()

            if sentiment not in ["positive", "negative", "neutral"]:
                return "neutral"

            return sentiment
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return "neutral"

    async def calculate_priority(
        self, email_content: str, sender: str, subject: str
    ) -> int:
        """
        Calculate email priority score (0-100)

        Args:
            email_content: Email body
            sender: Sender email
            subject: Email subject

        Returns:
            Priority score (0-100)
        """
        prompt = f"""Rate the priority of this email on a scale of 0-100, where:
0-20: Very low priority (newsletters, promotions)
21-40: Low priority (social, non-urgent)
41-60: Medium priority (regular correspondence)
61-80: High priority (work, important personal)
81-100: Urgent (requires immediate attention)

From: {sender}
Subject: {subject}
Body: {email_content[:500]}

Respond with ONLY a number between 0-100."""

        try:
            response = await self._generate(prompt, max_tokens=10)
            score = int(response.strip())
            return max(0, min(100, score))  # Clamp to 0-100
        except Exception as e:
            logger.error(f"Error calculating priority: {e}")
            return 50  # Default medium priority

    async def chat_completion(
        self, messages: List[Dict[str, str]], context: Optional[Dict] = None
    ) -> str:
        """
        Chat completion for conversational interface

        Args:
            messages: List of chat messages [{"role": "user", "content": "..."}]
            context: Optional context (email data, calendar data, etc.)

        Returns:
            AI response
        """
        try:
            # Add context if provided
            if context:
                context_str = f"\n\nContext:\n{self._format_context(context)}"
                messages[-1]["content"] += context_str

            if self.provider == "anthropic":
                # Convert to Claude format
                claude_messages = []
                for msg in messages:
                    role = "assistant" if msg["role"] == "assistant" else "user"
                    claude_messages.append({"role": role, "content": msg["content"]})

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=claude_messages,
                )
                return response.content[0].text

            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                return response.choices[0].message.content

            elif self.provider == "local":
                return await self._local_chat(messages)

        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return "I apologize, but I encountered an error processing your request."

    async def extract_event_from_email(self, email_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract calendar event information from email

        Args:
            email_content: Email text

        Returns:
            Event details or None
        """
        prompt = f"""Extract calendar event information from this email. If there's a meeting or event mentioned,
return it in this exact JSON format:
{{
    "title": "Event title",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "end_time": "HH:MM",
    "location": "Location if mentioned",
    "attendees": ["email1@example.com"]
}}

If no event is found, respond with: NO_EVENT

Email:
{email_content}

Event JSON:"""

        try:
            response = await self._generate(prompt, max_tokens=300)

            if "NO_EVENT" in response:
                return None

            # Parse JSON response
            import json

            event_data = json.loads(response)
            return event_data

        except Exception as e:
            logger.error(f"Error extracting event: {e}")
            return None

    async def _generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate completion from prompt

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        elif self.provider == "local":
            return await self._local_generate(prompt, max_tokens)

        raise ValueError(f"Unsupported provider: {self.provider}")

    async def _local_generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate using local AI endpoint (Ollama, LM Studio)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json().get("response", "")

    async def _local_chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat using local AI endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/chat",
                json={"model": self.model, "messages": messages},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")

    @staticmethod
    def _format_context(context: Dict) -> str:
        """Format context for AI"""
        formatted = []
        for key, value in context.items():
            formatted.append(f"{key}: {value}")
        return "\n".join(formatted)
