from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import ILoanRepository
from database.models import Loan


class LoanRepository(ILoanRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, loan_id: UUID) -> Optional[Loan]:
        result = await self._db.execute(
            select(Loan).where(Loan.id == loan_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID, loan_duration_days: int = 14) -> Loan:
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
        await self._db.commit()
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

    async def get_borrower_loans(self, borrower_id: UUID, status: Optional[str] = None) -> List[Loan]:
        query = select(Loan).where(Loan.borrower_id == borrower_id)
        if status:
            query = query.where(Loan.status == status)
        query = query.order_by(Loan.created_at.desc())
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
        result = await self._db.execute(
            select(func.count())
            .where(
                and_(
                    Loan.borrower_id == borrower_id,
                    Loan.status == "active"
                )
            )
        )
        return result.scalar() or 0
