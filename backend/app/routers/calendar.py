"""
Google Calendar API router
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from google.oauth2.credentials import Credentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from ..services import CalendarService

router = APIRouter(prefix="/calendar", tags=["calendar"])
logger = logging.getLogger(__name__)


class EventQuery(BaseModel):
    """Calendar event query"""

    calendar_id: str = "primary"
    time_min: Optional[datetime] = None
    time_max: Optional[datetime] = None
    max_results: int = 50
    query: str = ""


class CreateEventRequest(BaseModel):
    """Create event request"""

    summary: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    location: str = ""
    attendees: Optional[List[str]] = None
    calendar_id: str = "primary"
    timezone: str = "UTC"


class UpdateEventRequest(BaseModel):
    """Update event request"""

    event_id: str
    summary: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None
    calendar_id: str = "primary"


class QuickAddRequest(BaseModel):
    """Quick add event request"""

    text: str
    calendar_id: str = "primary"


def get_calendar_service(authorization: str = Header(...)) -> CalendarService:
    """Dependency to get Calendar service from auth header"""
    try:
        token = authorization.replace("Bearer ", "")
        credentials = Credentials(token=token)
        return CalendarService(credentials)
    except Exception as e:
        logger.error(f"Error creating Calendar service: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/events")
async def get_events(
    query: EventQuery,
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """
    Fetch calendar events

    Args:
        query: Event query parameters
        calendar_service: Calendar service instance

    Returns:
        List of events
    """
    try:
        events = await calendar_service.get_events(
            calendar_id=query.calendar_id,
            time_min=query.time_min,
            time_max=query.time_max,
            max_results=query.max_results,
            query=query.query,
        )
        return {"events": events, "total": len(events)}

    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/today")
async def get_today_events(
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """Get today's events"""
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        events = await calendar_service.get_events(
            time_min=today,
            time_max=tomorrow,
        )

        return {"events": events, "date": today.isoformat(), "total": len(events)}

    except Exception as e:
        logger.error(f"Error fetching today's events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/week")
async def get_week_events(
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """Get this week's events"""
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        next_week = today + timedelta(days=7)

        events = await calendar_service.get_events(
            time_min=today,
            time_max=next_week,
        )

        return {"events": events, "period": "week", "total": len(events)}

    except Exception as e:
        logger.error(f"Error fetching week events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}")
async def get_event(
    event_id: str,
    calendar_id: str = "primary",
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """Get specific event"""
    try:
        event = await calendar_service.get_event(event_id, calendar_id)
        return event
    except Exception as e:
        logger.error(f"Error fetching event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/create")
async def create_event(
    request: CreateEventRequest,
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """Create a new calendar event"""
    try:
        event = await calendar_service.create_event(
            summary=request.summary,
            start_time=request.start_time,
            end_time=request.end_time,
            description=request.description,
            location=request.location,
            attendees=request.attendees,
            calendar_id=request.calendar_id,
            timezone=request.timezone,
        )
        return event

    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/events/update")
async def update_event(
    request: UpdateEventRequest,
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """Update an existing event"""
    try:
        event = await calendar_service.update_event(
            event_id=request.event_id,
            summary=request.summary,
            start_time=request.start_time,
            end_time=request.end_time,
            description=request.description,
            location=request.location,
            calendar_id=request.calendar_id,
        )
        return event

    except Exception as e:
        logger.error(f"Error updating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    calendar_id: str = "primary",
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """Delete an event"""
    try:
        await calendar_service.delete_event(event_id, calendar_id)
        return {"status": "deleted", "event_id": event_id}

    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/quick-add")
async def quick_add_event(
    request: QuickAddRequest,
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """
    Quick add event using natural language

    Example: "Meeting tomorrow at 3pm"
    """
    try:
        event = await calendar_service.quick_add(request.text, request.calendar_id)
        return event

    except Exception as e:
        logger.error(f"Error quick adding event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendars")
async def list_calendars(
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """List all user's calendars"""
    try:
        calendars = await calendar_service.list_calendars()
        return {"calendars": calendars, "total": len(calendars)}

    except Exception as e:
        logger.error(f"Error listing calendars: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/free-busy")
async def get_free_busy(
    time_min: datetime,
    time_max: datetime,
    calendars: Optional[List[str]] = None,
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """Get free/busy information"""
    try:
        free_busy = await calendar_service.get_free_busy(
            time_min=time_min,
            time_max=time_max,
            calendars=calendars,
        )
        return free_busy

    except Exception as e:
        logger.error(f"Error fetching free/busy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
