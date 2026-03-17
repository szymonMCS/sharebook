import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_active_admin, get_db
from src.services.admin import AdminDashboardService
from database.repositories import UserRepository, BookRepository, LoanRepository, UserBookRepository
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter()

def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> AdminDashboardService:
    return AdminDashboardService(
        user_repo=UserRepository(db),
        book_repo=BookRepository(db),
        loan_repo=LoanRepository(db),
        user_book_repo=UserBookRepository(db)
    )

@router.get("", response_model=dict)
async def get_dashboard(
    current_user: User = Depends(get_current_active_admin),
    dashboard_service: AdminDashboardService = Depends(get_dashboard_service)
):
    stats = await dashboard_service.get_dashboard_stats()
    return {
        "success": True,
        "data": {
            "total_users": stats.total_users,
            "total_books": stats.total_books,
            "total_loans": stats.total_loans,
            "pending_requests": stats.pending_requests,
            "active_loans": stats.active_loans,
            "new_users_today": stats.new_users_today,
            "new_books_today": stats.new_books_today,
            "generated_at": stats.generated_at.isoformat()
        },
        "message": "Dashboard stats retrieved"
    }
