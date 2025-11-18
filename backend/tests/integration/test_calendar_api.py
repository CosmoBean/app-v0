"""
Integration tests for Calendar API
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime


@pytest.mark.integration
class TestCalendarAPI:
    """Test Calendar API endpoints"""

    def test_get_events(self, client, sample_calendar_event):
        """Test getting calendar events"""
        with patch("app.routers.calendar.CalendarService") as mock_service:
            mock_instance = Mock()
            mock_instance.get_events.return_value = [sample_calendar_event]
            mock_service.return_value = mock_instance

            response = client.post(
                "/calendar/events",
                json={"max_results": 10},
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "events" in data
            assert "total" in data

    def test_get_today_events(self, client, sample_calendar_event):
        """Test getting today's events"""
        with patch("app.routers.calendar.CalendarService") as mock_service:
            mock_instance = Mock()
            mock_instance.get_events.return_value = [sample_calendar_event]
            mock_service.return_value = mock_instance

            response = client.get(
                "/calendar/events/today",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "events" in data

    def test_get_week_events(self, client, sample_calendar_event):
        """Test getting week's events"""
        with patch("app.routers.calendar.CalendarService") as mock_service:
            mock_instance = Mock()
            mock_instance.get_events.return_value = [sample_calendar_event]
            mock_service.return_value = mock_instance

            response = client.get(
                "/calendar/events/week",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "events" in data

    def test_create_event(self, client):
        """Test creating calendar event"""
        with patch("app.routers.calendar.CalendarService") as mock_service:
            mock_instance = Mock()
            mock_instance.create_event.return_value = {
                "id": "new_event",
                "summary": "New Meeting"
            }
            mock_service.return_value = mock_instance

            response = client.post(
                "/calendar/events/create",
                json={
                    "summary": "New Meeting",
                    "start_time": "2024-01-15T14:00:00",
                    "end_time": "2024-01-15T15:00:00"
                },
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "new_event"

    def test_delete_event(self, client):
        """Test deleting event"""
        with patch("app.routers.calendar.CalendarService") as mock_service:
            mock_instance = Mock()
            mock_instance.delete_event.return_value = None
            mock_service.return_value = mock_instance

            response = client.delete(
                "/calendar/events/event123",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "deleted"

    def test_quick_add_event(self, client):
        """Test quick add with natural language"""
        with patch("app.routers.calendar.CalendarService") as mock_service:
            mock_instance = Mock()
            mock_instance.quick_add.return_value = {
                "id": "quick_event",
                "summary": "Meeting tomorrow at 3pm"
            }
            mock_service.return_value = mock_instance

            response = client.post(
                "/calendar/events/quick-add",
                json={"text": "Meeting tomorrow at 3pm"},
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "id" in data
