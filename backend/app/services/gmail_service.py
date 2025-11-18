"""
Gmail API service wrapper
"""
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class GmailService:
    """Wrapper for Gmail API operations"""

    def __init__(self, credentials: Credentials):
        """
        Initialize Gmail service with user credentials

        Args:
            credentials: Google OAuth2 credentials
        """
        self.credentials = credentials
        self.service = build("gmail", "v1", credentials=credentials)

    async def get_messages(
        self,
        max_results: int = 50,
        query: str = "",
        label_ids: Optional[List[str]] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch messages from Gmail

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
            label_ids: List of label IDs to filter by
            page_token: Token for pagination

        Returns:
            Dictionary with messages and next page token
        """
        try:
            params = {
                "userId": "me",
                "maxResults": max_results,
            }

            if query:
                params["q"] = query
            if label_ids:
                params["labelIds"] = label_ids
            if page_token:
                params["pageToken"] = page_token

            results = self.service.users().messages().list(**params).execute()

            messages = results.get("messages", [])
            next_page_token = results.get("nextPageToken")

            # Fetch full message details
            detailed_messages = []
            for msg in messages:
                try:
                    detailed_msg = await self.get_message(msg["id"])
                    detailed_messages.append(detailed_msg)
                except Exception as e:
                    logger.error(f"Error fetching message {msg['id']}: {e}")
                    continue

            return {
                "messages": detailed_messages,
                "next_page_token": next_page_token,
                "total": len(detailed_messages),
            }

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise

    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get full message details

        Args:
            message_id: Gmail message ID

        Returns:
            Message details dictionary
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            headers = {
                header["name"]: header["value"]
                for header in message["payload"].get("headers", [])
            }

            # Extract email body
            body_text = ""
            body_html = ""

            if "parts" in message["payload"]:
                for part in message["payload"]["parts"]:
                    if part["mimeType"] == "text/plain":
                        body_text = self._decode_body(part["body"].get("data", ""))
                    elif part["mimeType"] == "text/html":
                        body_html = self._decode_body(part["body"].get("data", ""))
            else:
                # Simple message
                body_data = message["payload"]["body"].get("data", "")
                body_text = self._decode_body(body_data)

            return {
                "id": message["id"],
                "thread_id": message["threadId"],
                "labels": message.get("labelIds", []),
                "snippet": message.get("snippet", ""),
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "cc": headers.get("Cc", ""),
                "bcc": headers.get("Bcc", ""),
                "date": headers.get("Date", ""),
                "body_text": body_text,
                "body_html": body_html,
                "internal_date": datetime.fromtimestamp(
                    int(message["internalDate"]) / 1000
                ),
            }

        except HttpError as error:
            logger.error(f"Error fetching message {message_id}: {error}")
            raise

    async def modify_message(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Modify message labels

        Args:
            message_id: Gmail message ID
            add_labels: Labels to add
            remove_labels: Labels to remove

        Returns:
            Modified message
        """
        try:
            body = {}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            message = (
                self.service.users()
                .messages()
                .modify(userId="me", id=message_id, body=body)
                .execute()
            )

            return message

        except HttpError as error:
            logger.error(f"Error modifying message {message_id}: {error}")
            raise

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        return await self.modify_message(message_id, remove_labels=["UNREAD"])

    async def mark_as_unread(self, message_id: str) -> Dict[str, Any]:
        """Mark message as unread"""
        return await self.modify_message(message_id, add_labels=["UNREAD"])

    async def star_message(self, message_id: str) -> Dict[str, Any]:
        """Star a message"""
        return await self.modify_message(message_id, add_labels=["STARRED"])

    async def unstar_message(self, message_id: str) -> Dict[str, Any]:
        """Unstar a message"""
        return await self.modify_message(message_id, remove_labels=["STARRED"])

    async def archive_message(self, message_id: str) -> Dict[str, Any]:
        """Archive a message"""
        return await self.modify_message(message_id, remove_labels=["INBOX"])

    async def trash_message(self, message_id: str) -> Dict[str, Any]:
        """Move message to trash"""
        try:
            message = (
                self.service.users()
                .messages()
                .trash(userId="me", id=message_id)
                .execute()
            )
            return message
        except HttpError as error:
            logger.error(f"Error trashing message {message_id}: {error}")
            raise

    async def delete_message(self, message_id: str) -> None:
        """Permanently delete a message"""
        try:
            self.service.users().messages().delete(userId="me", id=message_id).execute()
        except HttpError as error:
            logger.error(f"Error deleting message {message_id}: {error}")
            raise

    async def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an email

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients
            bcc: BCC recipients

        Returns:
            Sent message
        """
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {"raw": raw}

            sent_message = (
                self.service.users().messages().send(userId="me", body=body).execute()
            )

            return sent_message

        except HttpError as error:
            logger.error(f"Error sending message: {error}")
            raise

    async def create_label(self, name: str) -> Dict[str, Any]:
        """Create a new label"""
        try:
            label = {
                "name": name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            }
            created_label = (
                self.service.users().labels().create(userId="me", body=label).execute()
            )
            return created_label
        except HttpError as error:
            logger.error(f"Error creating label {name}: {error}")
            raise

    async def get_labels(self) -> List[Dict[str, Any]]:
        """Get all labels"""
        try:
            results = self.service.users().labels().list(userId="me").execute()
            return results.get("labels", [])
        except HttpError as error:
            logger.error(f"Error fetching labels: {error}")
            raise

    async def batch_modify(
        self, message_ids: List[str], add_labels: List[str] = None, remove_labels: List[str] = None
    ) -> None:
        """Batch modify multiple messages"""
        try:
            body = {"ids": message_ids}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            self.service.users().messages().batchModify(userId="me", body=body).execute()
        except HttpError as error:
            logger.error(f"Error batch modifying messages: {error}")
            raise

    @staticmethod
    def _decode_body(data: str) -> str:
        """Decode base64 encoded email body"""
        if not data:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8")
            return decoded
        except Exception as e:
            logger.error(f"Error decoding body: {e}")
            return ""
