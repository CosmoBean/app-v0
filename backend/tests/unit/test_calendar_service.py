"""
Tests for Calendar service
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.calendar_service import CalendarService


@pytest.mark.unit
class TestCalendarService:
    """Test Calendar service functionality"""

    @pytest.mark.asyncio
    async def test_get_events(self, mock_calendar_service, sample_calendar_event):
        """Test fetching calendar events"""
        mock_response = {"items": [sample_calendar_event]}

        with patch.object(
            mock_calendar_service.service.events(),
            "list",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_calendar_service.get_events()
            assert len(result) == 1
            assert result[0]["id"] == "event123"

    @pytest.mark.asyncio
    async def test_get_event(self, mock_calendar_service, sample_calendar_event):
        """Test getting single event"""
        with patch.object(
            mock_calendar_service.service.events(),
            "get",
            return_value=Mock(execute=Mock(return_value=sample_calendar_event))
        ):
            result = await mock_calendar_service.get_event("event123")
            assert result["id"] == "event123"
            assert result["summary"] == "Team Meeting"

    @pytest.mark.asyncio
    async def test_create_event(self, mock_calendar_service):
        """Test creating calendar event"""
        mock_response = {
            "id": "new_event",
            "summary": "New Meeting",
        }

        with patch.object(
            mock_calendar_service.service.events(),
            "insert",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_calendar_service.create_event(
                summary="New Meeting",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1)
            )
            assert result["id"] == "new_event"

    @pytest.mark.asyncio
    async def test_update_event(self, mock_calendar_service, sample_calendar_event):
        """Test updating calendar event"""
        updated_event = sample_calendar_event.copy()
        updated_event["summary"] = "Updated Meeting"

        with patch.object(mock_calendar_service, "get_event", return_value=sample_calendar_event):
            with patch.object(
                mock_calendar_service.service.events(),
                "update",
                return_value=Mock(execute=Mock(return_value=updated_event))
            ):
                result = await mock_calendar_service.update_event(
                    "event123",
                    summary="Updated Meeting"
                )
                assert result["summary"] == "Updated Meeting"

    @pytest.mark.asyncio
    async def test_delete_event(self, mock_calendar_service):
        """Test deleting calendar event"""
        with patch.object(
            mock_calendar_service.service.events(),
            "delete",
            return_value=Mock(execute=Mock(return_value={}))
        ):
            await mock_calendar_service.delete_event("event123")
            # No exception means success

    @pytest.mark.asyncio
    async def test_quick_add(self, mock_calendar_service):
        """Test quick add with natural language"""
        mock_response = {
            "id": "quick_event",
            "summary": "Meeting tomorrow at 3pm",
        }

        with patch.object(
            mock_calendar_service.service.events(),
            "quickAdd",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_calendar_service.quick_add("Meeting tomorrow at 3pm")
            assert result["id"] == "quick_event"

    @pytest.mark.asyncio
    async def test_get_free_busy(self, mock_calendar_service):
        """Test getting free/busy information"""
        mock_response = {
            "calendars": {
                "primary": {
                    "busy": [
                        {
                            "start": "2024-01-15T14:00:00-08:00",
                            "end": "2024-01-15T15:00:00-08:00",
                        }
                    ]
                }
            }
        }

        with patch.object(
            mock_calendar_service.service.freebusy(),
            "query",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_calendar_service.get_free_busy(
                time_min=datetime.now(),
                time_max=datetime.now() + timedelta(days=7)
            )
            assert "calendars" in result

    @pytest.mark.asyncio
    async def test_list_calendars(self, mock_calendar_service):
        """Test listing all calendars"""
        mock_response = {
            "items": [
                {"id": "primary", "summary": "Primary Calendar"},
                {"id": "work", "summary": "Work Calendar"},
            ]
        }

        with patch.object(
            mock_calendar_service.service.calendarList(),
            "list",
            return_value=Mock(execute=Mock(return_value=mock_response))
        ):
            result = await mock_calendar_service.list_calendars()
            assert len(result) == 2
