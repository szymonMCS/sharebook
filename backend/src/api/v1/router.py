from fastapi import APIRouter

from src.api.v1.endpoints.auth import auth_router, users_router
from src.api.v1.endpoints.books import books_router, community_router, covers_router
from src.api.v1.endpoints.loans import loans_router, loan_requests_router, messages_router
from src.api.v1.endpoints.system import health_router, ai_router, websocket_router
from src.api.v1.endpoints.library import library_browse_router, library_management_router
from src.api.v1.endpoints.admin import (
    admin_dashboard_router,
    admin_users_router,
    admin_books_router,
)

api_router = APIRouter()

# Auth
api_router.include_router(auth_router)
api_router.include_router(users_router)

# Health
api_router.include_router(health_router)

# Books
api_router.include_router(books_router)
api_router.include_router(library_browse_router, prefix="/my-books")
api_router.include_router(library_management_router, prefix="/my-books")
api_router.include_router(community_router)

# Loan Requests & Loans
api_router.include_router(loan_requests_router)
api_router.include_router(loans_router)
api_router.include_router(messages_router)

# Admin
api_router.include_router(admin_dashboard_router, prefix="/admin/dashboard")
api_router.include_router(admin_users_router, prefix="/admin/users")
api_router.include_router(admin_books_router, prefix="/admin/books")

# Covers
api_router.include_router(covers_router)

# System
api_router.include_router(ai_router)
api_router.include_router(websocket_router)
