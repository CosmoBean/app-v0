"""
API routers
"""
from .auth import router as auth_router
from .gmail import router as gmail_router
from .calendar import router as calendar_router
from .chat import router as chat_router

__all__ = [
    "auth_router",
    "gmail_router",
    "calendar_router",
    "chat_router",
]
