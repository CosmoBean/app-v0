"""
Authentication router - Google OAuth2
"""
from fastapi import APIRouter, HTTPException, Depends
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from pydantic import BaseModel
from typing import Optional
import logging
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


class AuthResponse(BaseModel):
    """Authentication response model"""

    access_token: str
    refresh_token: Optional[str]
    token_expiry: str
    user_email: str
    user_name: Optional[str]


class TokenRequest(BaseModel):
    """Token request model"""

    code: str


@router.get("/login")
async def login():
    """
    Initiate OAuth2 login flow

    Returns:
        Authorization URL for user to visit
    """
    try:
        # Create OAuth2 flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.google_scopes_list,
        )

        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )

        return {
            "authorization_url": authorization_url,
            "state": state,
        }

    except Exception as e:
        logger.error(f"Error initiating login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback", response_model=AuthResponse)
async def callback(token_request: TokenRequest):
    """
    Handle OAuth2 callback

    Args:
        token_request: Contains authorization code

    Returns:
        User credentials and profile
    """
    try:
        # Create OAuth2 flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.google_scopes_list,
        )

        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        # Exchange code for credentials
        flow.fetch_token(code=token_request.code)

        credentials = flow.credentials

        # Get user info
        from googleapiclient.discovery import build

        oauth_service = build("oauth2", "v2", credentials=credentials)
        user_info = oauth_service.userinfo().get().execute()

        return AuthResponse(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_expiry=credentials.expiry.isoformat() if credentials.expiry else "",
            user_email=user_info.get("email", ""),
            user_name=user_info.get("name"),
        )

    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token

    Args:
        refresh_token: Refresh token

    Returns:
        New access token
    """
    try:
        from google.auth.transport.requests import Request

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )

        credentials.refresh(Request())

        return {
            "access_token": credentials.token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else "",
        }

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout():
    """
    Logout user (client-side should clear tokens)

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}
