"""
Chat interface router - Conversational AI for email and calendar management
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from google.oauth2.credentials import Credentials
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
from ..services import GmailService, CalendarService, AIService, EmailOrganizer
from ..config import settings

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Chat message"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request"""

    messages: List[Message]
    include_email_context: bool = True
    include_calendar_context: bool = True
    max_context_items: int = 10


class ChatResponse(BaseModel):
    """Chat response"""

    message: str
    actions_taken: Optional[List[Dict[str, Any]]] = None
    context_used: Optional[Dict[str, Any]] = None


def get_gmail_service(authorization: str = Header(...)) -> GmailService:
    """Dependency to get Gmail service"""
    try:
        token = authorization.replace("Bearer ", "")
        credentials = Credentials(token=token)
        return GmailService(credentials)
    except Exception as e:
        logger.error(f"Error creating Gmail service: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


def get_calendar_service(authorization: str = Header(...)) -> CalendarService:
    """Dependency to get Calendar service"""
    try:
        token = authorization.replace("Bearer ", "")
        credentials = Credentials(token=token)
        return CalendarService(credentials)
    except Exception as e:
        logger.error(f"Error creating Calendar service: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


def get_ai_service() -> AIService:
    """Dependency to get AI service"""
    return AIService(
        provider=settings.DEFAULT_AI_PROVIDER,
        use_project_keys=True,
    )


@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
    calendar_service: CalendarService = Depends(get_calendar_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Process chat message and execute actions

    This endpoint:
    1. Analyzes user's request
    2. Gathers relevant context (emails, calendar)
    3. Executes actions (archive, schedule, etc.)
    4. Returns conversational response
    """
    try:
        # Get the latest user message
        latest_message = request.messages[-1].content

        # Build context
        context = await _build_context(
            latest_message,
            gmail_service,
            calendar_service,
            include_email=request.include_email_context,
            include_calendar=request.include_calendar_context,
            max_items=request.max_context_items,
        )

        # Detect intent and execute actions
        actions_taken = await _execute_actions(
            latest_message,
            context,
            gmail_service,
            calendar_service,
            ai_service,
        )

        # Generate conversational response
        messages_dict = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        response_text = await ai_service.chat_completion(
            messages=messages_dict,
            context=context,
        )

        return ChatResponse(
            message=response_text,
            actions_taken=actions_taken,
            context_used=context,
        )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _build_context(
    message: str,
    gmail_service: GmailService,
    calendar_service: CalendarService,
    include_email: bool = True,
    include_calendar: bool = True,
    max_items: int = 10,
) -> Dict[str, Any]:
    """Build context for AI from emails and calendar"""
    context = {}

    try:
        # Email context
        if include_email:
            # Detect what emails user is asking about
            query = _extract_email_query(message)

            emails = await gmail_service.get_messages(
                query=query,
                max_results=max_items,
            )

            context["emails"] = {
                "total": emails.get("total", 0),
                "items": [
                    {
                        "subject": email.get("subject"),
                        "from": email.get("from"),
                        "snippet": email.get("snippet"),
                        "date": email.get("date"),
                    }
                    for email in emails.get("messages", [])[:5]
                ],
            }

        # Calendar context
        if include_calendar:
            from datetime import timedelta

            # Get upcoming events
            events = await calendar_service.get_events(
                time_min=datetime.utcnow(),
                time_max=datetime.utcnow() + timedelta(days=7),
                max_results=max_items,
            )

            context["calendar"] = {
                "total": len(events),
                "items": [
                    {
                        "title": event.get("summary"),
                        "start": event.get("start", {}).get("dateTime"),
                        "end": event.get("end", {}).get("dateTime"),
                    }
                    for event in events[:5]
                ],
            }

    except Exception as e:
        logger.error(f"Error building context: {e}")

    return context


def _extract_email_query(message: str) -> str:
    """Extract Gmail query from natural language"""
    message_lower = message.lower()

    # Detect common patterns
    if "unread" in message_lower:
        return "is:unread"
    elif "starred" in message_lower or "important" in message_lower:
        return "is:starred"
    elif "today" in message_lower:
        return "newer_than:1d"
    elif "this week" in message_lower or "week" in message_lower:
        return "newer_than:7d"
    else:
        return ""


async def _execute_actions(
    message: str,
    context: Dict[str, Any],
    gmail_service: GmailService,
    calendar_service: CalendarService,
    ai_service: AIService,
) -> List[Dict[str, Any]]:
    """Detect intent and execute actions"""
    actions = []
    message_lower = message.lower()

    try:
        # Archive emails
        if "archive" in message_lower:
            query = _extract_email_query(message)
            emails = await gmail_service.get_messages(query=query, max_results=10)

            archived_count = 0
            for email in emails.get("messages", []):
                await gmail_service.archive_message(email["id"])
                archived_count += 1

            actions.append(
                {
                    "action": "archive",
                    "count": archived_count,
                    "query": query,
                }
            )

        # Mark as read
        elif "mark as read" in message_lower or "mark read" in message_lower:
            query = _extract_email_query(message)
            emails = await gmail_service.get_messages(query=query, max_results=10)

            marked_count = 0
            for email in emails.get("messages", []):
                await gmail_service.mark_as_read(email["id"])
                marked_count += 1

            actions.append(
                {
                    "action": "mark_as_read",
                    "count": marked_count,
                }
            )

        # Schedule meeting
        elif "schedule" in message_lower or "create meeting" in message_lower:
            # Use AI to extract event details
            event_data = await ai_service.extract_event_from_email(message)

            if event_data:
                from datetime import datetime

                event = await calendar_service.create_event(
                    summary=event_data.get("title"),
                    start_time=datetime.fromisoformat(
                        f"{event_data['date']} {event_data['start_time']}"
                    ),
                    end_time=datetime.fromisoformat(
                        f"{event_data['date']} {event_data['end_time']}"
                    ),
                    location=event_data.get("location", ""),
                )

                actions.append(
                    {
                        "action": "create_event",
                        "event": event,
                    }
                )

    except Exception as e:
        logger.error(f"Error executing actions: {e}")

    return actions


@router.post("/quick-action")
async def quick_action(
    action: str,
    parameters: Optional[Dict[str, Any]] = None,
    gmail_service: GmailService = Depends(get_gmail_service),
    calendar_service: CalendarService = Depends(get_calendar_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Execute predefined quick actions

    Actions:
    - summarize_unread: Summarize all unread emails
    - archive_newsletters: Archive all newsletters
    - show_today_schedule: Show today's calendar
    - find_free_time: Find free time slots
    """
    try:
        if action == "summarize_unread":
            emails = await gmail_service.get_messages(query="is:unread", max_results=20)

            summaries = []
            for email in emails.get("messages", [])[:10]:
                summary = await ai_service.summarize_email(email.get("body_text", ""))
                summaries.append(
                    {
                        "subject": email.get("subject"),
                        "from": email.get("from"),
                        "summary": summary,
                    }
                )

            return {"action": action, "summaries": summaries}

        elif action == "archive_newsletters":
            organizer = EmailOrganizer(gmail_service, ai_service)
            archived = await organizer.smart_archive_old_emails(
                days_old=7, categories=["newsletter", "promotions"]
            )

            return {"action": action, "archived_count": archived}

        elif action == "show_today_schedule":
            from datetime import timedelta

            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            events = await calendar_service.get_events(
                time_min=today,
                time_max=tomorrow,
            )

            return {"action": action, "events": events}

        elif action == "find_free_time":
            days = parameters.get("days", 7) if parameters else 7

            free_busy = await calendar_service.get_free_busy(
                time_min=datetime.utcnow(),
                time_max=datetime.utcnow() + timedelta(days=days),
            )

            return {"action": action, "free_busy": free_busy}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    except Exception as e:
        logger.error(f"Error executing quick action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions(
    gmail_service: GmailService = Depends(get_gmail_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Get AI-powered suggestions for inbox management

    Returns:
        List of suggested actions
    """
    try:
        # Get recent unread emails
        emails = await gmail_service.get_messages(query="is:unread", max_results=20)

        organizer = EmailOrganizer(gmail_service, ai_service)

        # Analyze and categorize
        suggestions = []

        # Count by category
        categories = {}
        for email in emails.get("messages", [])[:20]:
            processed = await organizer.process_email(email)
            category = processed.get("category", "unclassified")
            categories[category] = categories.get(category, 0) + 1

        # Generate suggestions
        if categories.get("newsletter", 0) > 5:
            suggestions.append(
                {
                    "type": "archive",
                    "description": f"You have {categories['newsletter']} newsletters. Archive old ones?",
                    "action": "archive_newsletters",
                }
            )

        if categories.get("important", 0) > 0:
            suggestions.append(
                {
                    "type": "attention",
                    "description": f"You have {categories['important']} important emails requiring attention.",
                    "action": "show_important",
                }
            )

        return {"suggestions": suggestions, "email_stats": categories}

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
