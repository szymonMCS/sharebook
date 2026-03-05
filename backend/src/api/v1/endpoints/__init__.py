from .users import router as users_router
from .health import router as health_router
from .auth import router as auth_router
from .books import router as books_router
from .library import router as library_router
from .loan_requests import router as loan_requests_router
from .loans import router as loans_router
from .covers import router as covers_router
from .websocket import router as websocket_router

__all__ = [
    "users_router",
    "health_router",
    "auth_router",
    "books_router",
    "library_router",
    "loan_requests_router",
    "loans_router",
    "covers_router",
    "websocket_router",
]
