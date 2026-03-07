import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Book, Loan, UserBook
from src.services.admin.interfaces import (
    IAdminDashboardService, 
    DashboardStats
)

logger = logging.getLogger(__name__)


class AdminDashboardService(IAdminDashboardService):
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def get_dashboard_stats(self) -> DashboardStats:
        total_users = await self._db.scalar(select(func.count()).select_from(User))
        total_books = await self._db.scalar(select(func.count()).select_from(Book))
        total_loans = await self._db.scalar(select(func.count()).select_from(Loan))
        pending_requests = await self._db.scalar(select(func.count()).select_from(UserBook).where(UserBook.status == "reserved"))
        active_loans = await self._db.scalar(select(func.count()).select_from(Loan).where(Loan.status == "active"))
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = await self._db.scalar(select(func.count()).select_from(User).where(User.created_at >= today))
        new_books_today = await self._db.scalar(select(func.count()).select_from(Book).where(Book.created_at >= today))
        
        return DashboardStats(
            total_users=total_users or 0,
            total_books=total_books or 0,
            total_loans=total_loans or 0,
            pending_requests=pending_requests or 0,
            active_loans=active_loans or 0,
            new_users_today=new_users_today or 0,
            new_books_today=new_books_today or 0,
            generated_at=datetime.now(timezone.utc)
        )
    
    async def get_user_stats(self, days: int = 30) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(func.date(User.created_at).label("date"), func.count().label("count"))
            .where(User.created_at >= since)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        result = await self._db.execute(stmt)
        daily_registrations = [{"date": str(row.date), "count": row.count} for row in result.all()]
        
        active_users = await self._db.scalar(select(func.count(func.distinct(Loan.borrower_id))).where(Loan.created_at >= since))
        return {
            "period_days": days,
            "daily_registrations": daily_registrations,
            "active_users": active_users or 0,
            "total_in_period": len(daily_registrations)
        }
    
    async def get_book_stats(self, days: int = 30) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(func.date(Book.created_at).label("date"), func.count().label("count"))
            .where(Book.created_at >= since)
            .group_by(func.date(Book.created_at))
            .order_by(func.date(Book.created_at))
        )
        result = await self._db.execute(stmt)
        daily_additions = [{"date": str(row.date), "count": row.count} for row in result.all()]
        popular_books_stmt = (
            select(Book.id, Book.title, Book.author, func.count(Loan.id).label("loan_count"))
            .join(Loan, Loan.user_book_id == Book.id)
            .where(Loan.created_at >= since)
            .group_by(Book.id, Book.title, Book.author)
            .order_by(func.count(Loan.id).desc())
            .limit(10)
        )
        popular_result = await self._db.execute(popular_books_stmt)
        popular_books = [
            {
                "id": str(row.id),
                "title": row.title,
                "author": row.author,
                "loan_count": row.loan_count
            }
            for row in popular_result.all()
        ]
        return {
            "period_days": days,
            "daily_additions": daily_additions,
            "popular_books": popular_books
        }
    
    async def get_loan_stats(self, days: int = 30) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        new_loans_stmt = (
            select(func.date(Loan.loan_date).label("date"), func.count().label("count"))
            .where(Loan.loan_date >= since)
            .group_by(func.date(Loan.loan_date))
            .order_by(func.date(Loan.loan_date))
        )
        new_loans_result = await self._db.execute(new_loans_stmt)
        daily_new_loans = [{"date": str(row.date), "count": row.count} for row in new_loans_result.all()]
        
        returned_loans_stmt = (
            select(func.date(Loan.return_date).label("date"), func.count().label("count"))
            .where(Loan.return_date >= since, Loan.return_date.isnot(None))
            .group_by(func.date(Loan.return_date))
            .order_by(func.date(Loan.return_date))
        )
        
        returned_result = await self._db.execute(returned_loans_stmt)
        daily_returned = [{"date": str(row.date), "count": row.count} for row in returned_result.all()]
        
        avg_duration_stmt = (
            select(func.avg(func.extract('epoch', Loan.return_date - Loan.loan_date) / 86400))
            .where(Loan.return_date.isnot(None), Loan.loan_date >= since)
        )
        
        avg_duration = await self._db.scalar(avg_duration_stmt)
        
        return {
            "period_days": days,
            "daily_new_loans": daily_new_loans,
            "daily_returned": daily_returned,
            "average_loan_duration_days": round(avg_duration, 2) if avg_duration else 0
        }
