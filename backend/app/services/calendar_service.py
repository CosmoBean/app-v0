"""
Google Calendar API service wrapper
"""
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CalendarService:
    """Wrapper for Google Calendar API operations"""

    def __init__(self, credentials: Credentials):
        """
        Initialize Calendar service with user credentials

        Args:
            credentials: Google OAuth2 credentials
        """
        self.credentials = credentials
        self.service = build("calendar", "v3", credentials=credentials)

    async def get_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 50,
        query: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events

        Args:
            calendar_id: Calendar ID (default: primary)
            time_min: Start datetime for events
            time_max: End datetime for events
            max_results: Maximum number of events
            query: Search query

        Returns:
            List of events
        """
        try:
            # Default to today if not specified
            if not time_min:
                time_min = datetime.utcnow()
            if not time_max:
                time_max = time_min + timedelta(days=30)

            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min.isoformat() + "Z",
                    timeMax=time_max.isoformat() + "Z",
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                    q=query if query else None,
                )
                .execute()
            )

            events = events_result.get("items", [])
            return events

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            raise

    async def get_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Get specific event details

        Args:
            event_id: Event ID
            calendar_id: Calendar ID

        Returns:
            Event details
        """
        try:
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )
            return event
        except HttpError as error:
            logger.error(f"Error fetching event {event_id}: {error}")
            raise

    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = "",
        attendees: List[str] = None,
        calendar_id: str = "primary",
        timezone: str = "UTC",
    ) -> Dict[str, Any]:
        """
        Create a new calendar event

        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            attendees: List of attendee emails
            calendar_id: Calendar ID
            timezone: Timezone

        Returns:
            Created event
        """
        try:
            event = {
                "summary": summary,
                "description": description,
                "location": location,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": timezone,
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": timezone,
                },
            }

            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]

            created_event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )

            return created_event

        except HttpError as error:
            logger.error(f"Error creating event: {error}")
            raise

    async def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """Update an existing event"""
        try:
            # Fetch existing event
            event = await self.get_event(event_id, calendar_id)

            # Update fields
            if summary:
                event["summary"] = summary
            if description is not None:
                event["description"] = description
            if location is not None:
                event["location"] = location
            if start_time:
                event["start"]["dateTime"] = start_time.isoformat()
            if end_time:
                event["end"]["dateTime"] = end_time.isoformat()

            updated_event = (
                self.service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )

            return updated_event

        except HttpError as error:
            logger.error(f"Error updating event {event_id}: {error}")
            raise

    async def delete_event(self, event_id: str, calendar_id: str = "primary") -> None:
        """Delete an event"""
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
        except HttpError as error:
            logger.error(f"Error deleting event {event_id}: {error}")
            raise

    async def get_free_busy(
        self,
        time_min: datetime,
        time_max: datetime,
        calendars: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Get free/busy information

        Args:
            time_min: Start time
            time_max: End time
            calendars: List of calendar IDs to check (default: primary)

        Returns:
            Free/busy information
        """
        try:
            if not calendars:
                calendars = ["primary"]

            body = {
                "timeMin": time_min.isoformat() + "Z",
                "timeMax": time_max.isoformat() + "Z",
                "items": [{"id": cal_id} for cal_id in calendars],
            }

            free_busy = self.service.freebusy().query(body=body).execute()
            return free_busy

        except HttpError as error:
            logger.error(f"Error fetching free/busy: {error}")
            raise

    async def list_calendars(self) -> List[Dict[str, Any]]:
        """List all calendars"""
        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get("items", [])
        except HttpError as error:
            logger.error(f"Error listing calendars: {error}")
            raise

    async def quick_add(self, text: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Quick add event using natural language

        Args:
            text: Natural language event description (e.g., "Meeting tomorrow at 3pm")
            calendar_id: Calendar ID

        Returns:
            Created event
        """
        try:
            event = (
                self.service.events()
                .quickAdd(calendarId=calendar_id, text=text)
                .execute()
            )
            return event
        except HttpError as error:
            logger.error(f"Error quick adding event: {error}")
            raise
