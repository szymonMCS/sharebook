from .dashboard import router as admin_dashboard_router
from .users import router as admin_users_router
from .books import router as admin_books_router

__all__ = ["admin_dashboard_router", "admin_users_router", "admin_books_router"]
