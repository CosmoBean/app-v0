"""
Integration tests for authentication API
"""
import pytest
from unittest.mock import patch, Mock


@pytest.mark.integration
class TestAuthAPI:
    """Test authentication API endpoints"""

    def test_login_endpoint(self, client):
        """Test login initiation endpoint"""
        response = client.get("/auth/login")

        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "state" in data
        assert "accounts.google.com" in data["authorization_url"]

    def test_callback_endpoint(self, client):
        """Test OAuth callback endpoint"""
        with patch("app.routers.auth.Flow") as mock_flow:
            # Mock the OAuth flow
            mock_flow_instance = Mock()
            mock_credentials = Mock()
            mock_credentials.token = "test_token"
            mock_credentials.refresh_token = "test_refresh"
            mock_credentials.expiry = None

            mock_flow_instance.credentials = mock_credentials
            mock_flow.from_client_config.return_value = mock_flow_instance

            # Mock user info
            with patch("app.routers.auth.build") as mock_build:
                mock_service = Mock()
                mock_service.userinfo().get().execute.return_value = {
                    "email": "test@example.com",
                    "name": "Test User"
                }
                mock_build.return_value = mock_service

                response = client.post(
                    "/auth/callback",
                    json={"code": "test_authorization_code"}
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "user_email" in data

    def test_logout_endpoint(self, client):
        """Test logout endpoint"""
        response = client.post("/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
