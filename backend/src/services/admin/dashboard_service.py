import logging
from datetime import datetime, timezone
from database.interfaces import IUserRepository, IBookRepository, ILoanRepository, IUserBookRepository
from src.services.interfaces import (
    IAdminDashboardService, 
    DashboardStats
)

logger = logging.getLogger(__name__)


class AdminDashboardService(IAdminDashboardService):
    def __init__(
        self,
        user_repo: IUserRepository,
        book_repo: IBookRepository,
        loan_repo: ILoanRepository,
        user_book_repo: IUserBookRepository
    ):
        self._user_repo = user_repo
        self._book_repo = book_repo
        self._loan_repo = loan_repo
        self._user_book_repo = user_book_repo
    
    async def get_dashboard_stats(self) -> DashboardStats:
        total_users = await self._user_repo.count_all()
        total_books = await self._book_repo.count_all()
        total_loans = await self._loan_repo.count_all()
        pending_requests = await self._user_book_repo.count_by_status("reserved")
        active_loans = await self._loan_repo.count_active()
        
        from datetime import timedelta
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = await self._user_repo.count_new_since(today)
        new_books_today = await self._book_repo.count_new_since(today)
        
        return DashboardStats(
            total_users=total_users,
            total_books=total_books,
            total_loans=total_loans,
            pending_requests=pending_requests,
            active_loans=active_loans,
            new_users_today=new_users_today,
            new_books_today=new_books_today,
            generated_at=datetime.now(timezone.utc)
        )
    
    async def get_user_stats(self, days: int = 30) -> dict:
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        daily_registrations = await self._user_repo.get_daily_registrations(days)
        active_users = await self._user_repo.count_active_borrowers(since)
        
        return {
            "period_days": days,
            "daily_registrations": daily_registrations,
            "active_users": active_users,
            "total_in_period": len(daily_registrations)
        }
    
    async def get_book_stats(self, days: int = 30) -> dict:
        daily_additions = await self._book_repo.get_daily_additions(days)
        popular_books = await self._book_repo.get_popular_books(days, limit=10)
        
        return {
            "period_days": days,
            "daily_additions": daily_additions,
            "popular_books": popular_books
        }
    
    async def get_loan_stats(self, days: int = 30) -> dict:
        stats = await self._loan_repo.get_daily_stats(days)
        avg_duration = await self._loan_repo.get_average_duration(days)
        
        return {
            "period_days": days,
            "daily_new_loans": stats["daily_new"],
            "daily_returned": stats["daily_returned"],
            "average_loan_duration_days": round(avg_duration, 2) if avg_duration else 0
        }
