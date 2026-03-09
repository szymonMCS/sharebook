from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import ILoanRepository
from database.models import Loan
import logging

logger = logging.getLogger(__name__)


class LoanRepository(ILoanRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, loan_id: UUID) -> Optional[Loan]:
        result = await self._db.execute(select(Loan).where(Loan.id == loan_id))
        return result.scalar_one_or_none()

    async def create(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID, loan_duration_days: int = 14, commit: bool = True) -> Loan:
        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=loan_duration_days)

        loan = Loan(
            user_book_id=user_book_id,
            borrower_id=borrower_id,
            lender_id=lender_id,
            status="active",
            loan_date=now,
            due_date=due_date,
            return_date=None,
            created_at=now,
            updated_at=now,
        )
        self._db.add(loan)
        if commit:
            await self._db.commit()
            await self._db.refresh(loan)
        else:
            await self._db.flush()
            await self._db.refresh(loan)
        return loan

    async def mark_returned(self, loan_id: UUID) -> Optional[Loan]:
        loan = await self.get_by_id(loan_id)
        if not loan:
            return None

        loan.status = "returned"
        loan.return_date = datetime.now(timezone.utc)
        loan.updated_at = datetime.now(timezone.utc)

        await self._db.commit()
        await self._db.refresh(loan)
        return loan

    async def delete(self, loan_id: UUID) -> bool:
        loan = await self.get_by_id(loan_id)
        if not loan:
            return False
        
        await self._db.delete(loan)
        await self._db.commit()
        return True

    async def get_borrower_loans(self, borrower_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Loan]:
        query = select(Loan).where(Loan.borrower_id == borrower_id)
        if status:
            query = query.where(Loan.status == status)
        query = query.order_by(Loan.created_at.desc()).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_lender_loans(self, lender_id: UUID, status: Optional[str] = None) -> List[Loan]:
        query = select(Loan).where(Loan.lender_id == lender_id)
        if status:
            query = query.where(Loan.status == status)
        query = query.order_by(Loan.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def count_active_for_borrower(self, borrower_id: UUID) -> int:
        result = await self._db.execute(select(func.count()).where(and_(Loan.borrower_id == borrower_id, Loan.status == "active")))
        return result.scalar() or 0

    async def count_all(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Loan))
        return result.scalar() or 0

    async def count_active(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Loan).where(Loan.status == "active"))
        return result.scalar() or 0

    async def count_by_status(self, status: str) -> int:
        result = await self._db.execute(select(func.count()).select_from(Loan).where(Loan.status == status))
        return result.scalar() or 0

    async def get_daily_stats(self, days: int) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        new_stmt = (
            select(func.date(Loan.loan_date).label("date"), func.count().label("count"))
            .where(Loan.loan_date >= since)
            .group_by(func.date(Loan.loan_date))
            .order_by(func.date(Loan.loan_date))
        )
        new_result = await self._db.execute(new_stmt)
        daily_new = [{"date": str(row.date), "count": row.count} for row in new_result.all()]
        
        returned_stmt = (
            select(func.date(Loan.return_date).label("date"), func.count().label("count"))
            .where(Loan.return_date >= since, Loan.return_date.isnot(None))
            .group_by(func.date(Loan.return_date))
            .order_by(func.date(Loan.return_date))
        )
        returned_result = await self._db.execute(returned_stmt)
        daily_returned = [{"date": str(row.date), "count": row.count} for row in returned_result.all()]
        
        return {
            "daily_new": daily_new,
            "daily_returned": daily_returned
        }

    async def get_average_duration(self, days: int) -> Optional[float]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(func.avg(func.extract('epoch', Loan.return_date - Loan.loan_date) / 86400))
            .where(Loan.return_date.isnot(None), Loan.loan_date >= since)
        )
        result = await self._db.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg is not None else None
