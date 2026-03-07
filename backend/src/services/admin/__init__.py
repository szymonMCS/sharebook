from src.services.admin.interfaces import (
    IAdminDashboardService,
    IUserAdminService,
    IBookAdminService,
    DashboardStats,
    UserListResult,
    BookListResult
)
from src.services.admin.dashboard_service import AdminDashboardService
from src.services.admin.user_admin_service import UserAdminService
from src.services.admin.book_admin_service import BookAdminService

__all__ = [
    "IAdminDashboardService",
    "IUserAdminService",
    "IBookAdminService",
    "DashboardStats",
    "UserListResult",
    "BookListResult",
    "AdminDashboardService",
    "UserAdminService",
    "BookAdminService",
]
