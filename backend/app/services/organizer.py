"""
Email organization and AI processing orchestration
"""
from typing import List, Dict, Optional, Any
from .ai_service import AIService
from .gmail_service import GmailService
from ..models.email import EmailCategory
import logging
import asyncio

logger = logging.getLogger(__name__)


class EmailOrganizer:
    """
    Orchestrates AI-powered email organization
    """

    def __init__(self, gmail_service: GmailService, ai_service: AIService):
        """
        Initialize email organizer

        Args:
            gmail_service: Gmail service instance
            ai_service: AI service instance
        """
        self.gmail = gmail_service
        self.ai = ai_service

    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single email with AI

        Args:
            email_data: Email data from Gmail API

        Returns:
            Processed email data with AI-generated fields
        """
        try:
            email_content = email_data.get("body_text", "")
            subject = email_data.get("subject", "")
            sender = email_data.get("from", "")

            # Run AI tasks in parallel for speed
            results = await asyncio.gather(
                self.ai.summarize_email(email_content),
                self.ai.categorize_email(email_content, sender, subject),
                self.ai.extract_tags(email_content, subject),
                self.ai.analyze_sentiment(email_content),
                self.ai.calculate_priority(email_content, sender, subject),
                return_exceptions=True,
            )

            # Unpack results
            summary = results[0] if not isinstance(results[0], Exception) else ""
            category = results[1] if not isinstance(results[1], Exception) else "unclassified"
            tags = results[2] if not isinstance(results[2], Exception) else []
            sentiment = results[3] if not isinstance(results[3], Exception) else "neutral"
            priority = results[4] if not isinstance(results[4], Exception) else 50

            # Add AI-generated fields to email data
            email_data["summary"] = summary
            email_data["category"] = category
            email_data["ai_tags"] = tags
            email_data["sentiment"] = sentiment
            email_data["priority_score"] = priority

            return email_data

        except Exception as e:
            logger.error(f"Error processing email {email_data.get('id')}: {e}")
            return email_data

    async def process_batch(
        self, email_list: List[Dict[str, Any]], batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Process multiple emails in batches

        Args:
            email_list: List of email data
            batch_size: Number of emails to process concurrently

        Returns:
            List of processed emails
        """
        processed_emails = []

        # Process in batches to avoid rate limits
        for i in range(0, len(email_list), batch_size):
            batch = email_list[i : i + batch_size]

            tasks = [self.process_email(email) for email in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if not isinstance(result, Exception):
                    processed_emails.append(result)
                else:
                    logger.error(f"Batch processing error: {result}")

            # Small delay between batches
            if i + batch_size < len(email_list):
                await asyncio.sleep(0.5)

        return processed_emails

    async def auto_categorize_and_label(
        self, email_data: Dict[str, Any], apply_labels: bool = True
    ) -> Dict[str, Any]:
        """
        Automatically categorize email and apply Gmail labels

        Args:
            email_data: Email data
            apply_labels: Whether to apply labels to Gmail

        Returns:
            Updated email data
        """
        # Process email with AI
        processed = await self.process_email(email_data)

        if apply_labels:
            category = processed.get("category", "unclassified")
            gmail_id = email_data.get("id")

            # Map categories to actions
            category_actions = {
                "newsletter": lambda: self._handle_newsletter(gmail_id),
                "promotions": lambda: self._handle_promotions(gmail_id),
                "spam": lambda: self._handle_spam(gmail_id),
                "important": lambda: self._handle_important(gmail_id),
            }

            action = category_actions.get(category)
            if action:
                try:
                    await action()
                except Exception as e:
                    logger.error(f"Error applying labels: {e}")

        return processed

    async def _handle_newsletter(self, gmail_id: str):
        """Handle newsletter emails"""
        # Could auto-archive, apply label, etc.
        await self.gmail.modify_message(gmail_id, add_labels=["Newsletter"])

    async def _handle_promotions(self, gmail_id: str):
        """Handle promotional emails"""
        await self.gmail.modify_message(gmail_id, add_labels=["Promotions"])

    async def _handle_spam(self, gmail_id: str):
        """Handle spam emails"""
        # Mark as spam or trash
        await self.gmail.trash_message(gmail_id)

    async def _handle_important(self, gmail_id: str):
        """Handle important emails"""
        await self.gmail.modify_message(gmail_id, add_labels=["IMPORTANT", "STARRED"])

    async def extract_action_items(self, email_content: str) -> List[str]:
        """
        Extract action items from email

        Args:
            email_content: Email text

        Returns:
            List of action items
        """
        prompt = f"""Extract action items from this email. Return as a bulleted list.
If no action items, return: NO_ACTION_ITEMS

Email:
{email_content}

Action Items:"""

        try:
            response = await self.ai._generate(prompt, max_tokens=200)

            if "NO_ACTION_ITEMS" in response:
                return []

            # Parse bulleted list
            items = [
                line.strip("- •*").strip()
                for line in response.split("\n")
                if line.strip()
            ]
            return items

        except Exception as e:
            logger.error(f"Error extracting action items: {e}")
            return []

    async def suggest_reply(self, email_content: str, tone: str = "professional") -> str:
        """
        Generate suggested email reply

        Args:
            email_content: Original email
            tone: Reply tone (professional, casual, friendly)

        Returns:
            Suggested reply
        """
        prompt = f"""Generate a {tone} email reply to the following email.
Keep it concise and appropriate.

Email:
{email_content}

Reply:"""

        try:
            reply = await self.ai._generate(prompt, max_tokens=300)
            return reply.strip()
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return ""

    async def find_similar_emails(
        self, email_data: Dict[str, Any], all_emails: List[Dict[str, Any]], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar emails based on content and category

        Args:
            email_data: Reference email
            all_emails: List of all emails to search
            limit: Maximum number of similar emails

        Returns:
            List of similar emails
        """
        reference_category = email_data.get("category")
        reference_tags = set(email_data.get("ai_tags", []))
        reference_sender = email_data.get("from", "")

        similar = []

        for email in all_emails:
            if email.get("id") == email_data.get("id"):
                continue

            similarity_score = 0

            # Same category
            if email.get("category") == reference_category:
                similarity_score += 3

            # Same sender
            if email.get("from") == reference_sender:
                similarity_score += 2

            # Overlapping tags
            email_tags = set(email.get("ai_tags", []))
            overlap = len(reference_tags & email_tags)
            similarity_score += overlap

            if similarity_score > 0:
                similar.append({"email": email, "score": similarity_score})

        # Sort by similarity score
        similar.sort(key=lambda x: x["score"], reverse=True)

        return [item["email"] for item in similar[:limit]]

    async def smart_archive_old_emails(
        self, days_old: int = 30, categories: List[str] = None
    ) -> int:
        """
        Intelligently archive old emails from specific categories

        Args:
            days_old: Archive emails older than this many days
            categories: Categories to archive (e.g., ['newsletter', 'promotions'])

        Returns:
            Number of emails archived
        """
        from datetime import datetime, timedelta

        if not categories:
            categories = ["newsletter", "promotions"]

        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Fetch emails
        query = f"before:{cutoff_date.strftime('%Y/%m/%d')}"
        result = await self.gmail.get_messages(query=query, max_results=100)

        emails_to_archive = []

        for email in result.get("messages", []):
            # Check if email matches categories
            processed = await self.process_email(email)
            if processed.get("category") in categories:
                emails_to_archive.append(email["id"])

        # Batch archive
        if emails_to_archive:
            await self.gmail.batch_modify(
                emails_to_archive, remove_labels=["INBOX"]
            )

        return len(emails_to_archive)
