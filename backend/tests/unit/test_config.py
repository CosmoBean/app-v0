"""
Tests for configuration management
"""
import pytest
from app.config import Settings, get_settings


@pytest.mark.unit
class TestConfig:
    """Test configuration management"""

    def test_settings_load(self):
        """Test settings can be loaded"""
        settings = get_settings()
        assert settings is not None
        assert settings.APP_NAME == "Gmail AI Organizer"

    def test_google_scopes_list(self):
        """Test Google scopes are parsed correctly"""
        settings = get_settings()
        scopes = settings.google_scopes_list
        assert isinstance(scopes, list)
        assert len(scopes) >= 2
        assert "gmail" in scopes[0].lower()

    def test_cors_origins_list(self):
        """Test CORS origins are parsed correctly"""
        settings = get_settings()
        origins = settings.cors_origins_list
        assert isinstance(origins, list)
        assert len(origins) >= 1

    def test_settings_singleton(self):
        """Test settings is a singleton"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_environment_defaults(self):
        """Test default environment values"""
        settings = get_settings()
        assert settings.MAX_EMAILS_PER_REQUEST == 50
        assert settings.EMAIL_BATCH_SIZE == 10
        assert settings.CALENDAR_LOOKAHEAD_DAYS == 30
