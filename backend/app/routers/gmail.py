"""
Gmail API router
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from google.oauth2.credentials import Credentials
from pydantic import BaseModel
from typing import List, Optional
import logging
from ..services import GmailService, AIService, EmailOrganizer
from ..config import settings

router = APIRouter(prefix="/gmail", tags=["gmail"])
logger = logging.getLogger(__name__)


class EmailQuery(BaseModel):
    """Email query parameters"""

    max_results: int = 50
    query: str = ""
    label_ids: Optional[List[str]] = None


class ModifyLabelsRequest(BaseModel):
    """Request to modify email labels"""

    message_id: str
    add_labels: Optional[List[str]] = None
    remove_labels: Optional[List[str]] = None


class SendEmailRequest(BaseModel):
    """Send email request"""

    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None


class BatchProcessRequest(BaseModel):
    """Batch process emails request"""

    message_ids: Optional[List[str]] = None
    query: Optional[str] = None
    max_results: int = 50
    auto_categorize: bool = True
    apply_labels: bool = False


def get_gmail_service(authorization: str = Header(...)) -> GmailService:
    """Dependency to get Gmail service from auth header"""
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")

        credentials = Credentials(token=token)
        return GmailService(credentials)

    except Exception as e:
        logger.error(f"Error creating Gmail service: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


def get_ai_service() -> AIService:
    """Dependency to get AI service"""
    # For now, use project keys. In production, fetch user preferences from DB
    return AIService(
        provider=settings.DEFAULT_AI_PROVIDER,
        use_project_keys=True,
    )


@router.post("/messages")
async def get_messages(
    query: EmailQuery,
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """
    Fetch emails from Gmail

    Args:
        query: Email query parameters
        gmail_service: Gmail service instance

    Returns:
        List of emails
    """
    try:
        result = await gmail_service.get_messages(
            max_results=query.max_results,
            query=query.query,
            label_ids=query.label_ids,
        )
        return result

    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{message_id}")
async def get_message(
    message_id: str,
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """Get single email details"""
    try:
        message = await gmail_service.get_message(message_id)
        return message
    except Exception as e:
        logger.error(f"Error fetching message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/modify")
async def modify_labels(
    request: ModifyLabelsRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """Modify email labels"""
    try:
        result = await gmail_service.modify_message(
            request.message_id,
            add_labels=request.add_labels,
            remove_labels=request.remove_labels,
        )
        return result
    except Exception as e:
        logger.error(f"Error modifying labels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/send")
async def send_email(
    request: SendEmailRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """Send an email"""
    try:
        result = await gmail_service.send_message(
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            bcc=request.bcc,
        )
        return result
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/{message_id}/archive")
async def archive_message(
    message_id: str,
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """Archive an email"""
    try:
        result = await gmail_service.archive_message(message_id)
        return {"status": "archived", "message_id": message_id}
    except Exception as e:
        logger.error(f"Error archiving message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/{message_id}/trash")
async def trash_message(
    message_id: str,
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """Move email to trash"""
    try:
        result = await gmail_service.trash_message(message_id)
        return {"status": "trashed", "message_id": message_id}
    except Exception as e:
        logger.error(f"Error trashing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/labels")
async def get_labels(gmail_service: GmailService = Depends(get_gmail_service)):
    """Get all Gmail labels"""
    try:
        labels = await gmail_service.get_labels()
        return {"labels": labels}
    except Exception as e:
        logger.error(f"Error fetching labels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-batch")
async def process_batch(
    request: BatchProcessRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Process multiple emails with AI

    Args:
        request: Batch process parameters
        gmail_service: Gmail service
        ai_service: AI service

    Returns:
        Processed emails with AI-generated data
    """
    try:
        organizer = EmailOrganizer(gmail_service, ai_service)

        # Fetch emails
        if request.message_ids:
            emails = []
            for msg_id in request.message_ids:
                email = await gmail_service.get_message(msg_id)
                emails.append(email)
        else:
            result = await gmail_service.get_messages(
                max_results=request.max_results,
                query=request.query or "",
            )
            emails = result.get("messages", [])

        # Process with AI
        if request.auto_categorize:
            processed = []
            for email in emails:
                processed_email = await organizer.auto_categorize_and_label(
                    email, apply_labels=request.apply_labels
                )
                processed.append(processed_email)
        else:
            processed = await organizer.process_batch(emails)

        return {
            "total": len(processed),
            "emails": processed,
        }

    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/{message_id}/summarize")
async def summarize_email(
    message_id: str,
    gmail_service: GmailService = Depends(get_gmail_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """Summarize a single email"""
    try:
        email = await gmail_service.get_message(message_id)
        summary = await ai_service.summarize_email(email.get("body_text", ""))

        return {
            "message_id": message_id,
            "subject": email.get("subject"),
            "summary": summary,
        }

    except Exception as e:
        logger.error(f"Error summarizing email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
