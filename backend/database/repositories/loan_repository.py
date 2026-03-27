import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.models import Loan, UserBook
from database.repositories.base import BaseRepository
from database.interfaces import ILoanRepository


class LoanRepository(BaseRepository[Loan], ILoanRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Loan, db)
    
    async def delete(self, loan_id: uuid.UUID) -> bool:  # type: ignore[override]
        return await super().delete(loan_id)
    
    async def get_by_id(self, loan_id: uuid.UUID) -> Optional[Loan]:
        return await self.get(loan_id)
    
    async def get_by_id_with_relations(self, loan_id: uuid.UUID) -> Optional[Loan]:
        result = await self._db.execute(
            select(Loan)
            .options(
                joinedload(Loan.borrower),
                joinedload(Loan.lender),
                joinedload(Loan.user_book).joinedload(UserBook.book)
            )
            .where(Loan.id == loan_id)
        )
        return result.scalar_one_or_none()
    
    async def get_borrower_loans(self, borrower_id: uuid.UUID, status: Optional[str] = None) -> List[Loan]:
        query = select(Loan).where(Loan.borrower_id == borrower_id)
        if status:
            query = query.where(Loan.status == status)
        query = query.order_by(Loan.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_borrower_loans_with_details(self, borrower_id: uuid.UUID, status: Optional[str] = None) -> List[Loan]:
        query = (
            select(Loan)
            .options(
                joinedload(Loan.user_book).joinedload(UserBook.book),
                joinedload(Loan.lender),
                joinedload(Loan.borrower)
            )
            .where(Loan.borrower_id == borrower_id)
        )
        if status:
            query = query.where(Loan.status == status)
        query = query.order_by(Loan.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_lender_loans(self, lender_id: uuid.UUID, status: Optional[str] = None) -> List[Loan]:
        query = select(Loan).where(Loan.lender_id == lender_id)
        if status:
            query = query.where(Loan.status == status)
        query = query.order_by(Loan.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_lender_loans_with_details(self, lender_id: uuid.UUID, status: Optional[str] = None) -> List[Loan]:
        query = (
            select(Loan)
            .options(
                joinedload(Loan.user_book).joinedload(UserBook.book),
                joinedload(Loan.lender),
                joinedload(Loan.borrower)
            )
            .where(Loan.lender_id == lender_id)
        )
        if status:
            query = query.where(Loan.status == status)
        query = query.order_by(Loan.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_active_loans_for_user_book(self, user_book_id: uuid.UUID,) -> List[Loan]:
        result = await self._db.execute(
            select(Loan)
            .where(and_(Loan.user_book_id == user_book_id, Loan.status == "active"))
        )
        return list(result.scalars().all())
    
    async def has_active_loan(self, user_book_id: uuid.UUID,) -> bool:
        result = await self._db.execute(
            select(func.count())
            .where(and_(Loan.user_book_id == user_book_id, Loan.status == "active"))
        )
        count = result.scalar()
        return count > 0 if count is not None else False
    
    async def count_active_for_borrower(self, borrower_id: uuid.UUID) -> int:
        return await self.count_active_loans_for_borrower(borrower_id)
    
    async def count_active_loans_for_borrower(self, borrower_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .where(and_(Loan.borrower_id == borrower_id, Loan.status == "active"))
        )
        return result.scalar() or 0
    
    async def count_active_loans_for_lender(self, lender_id: uuid.UUID,) -> int:
        result = await self._db.execute(
            select(func.count())
            .where(and_(Loan.lender_id == lender_id, Loan.status == "active"))
        )
        return result.scalar() or 0
    
    async def create(self, user_book_id: uuid.UUID, borrower_id: uuid.UUID, lender_id: uuid.UUID, loan_duration_days: int = 14,) -> Loan:  # type: ignore[override]
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
    
    async def mark_returned(self, loan_id: uuid.UUID) -> Optional[Loan]:
        return await self.mark_as_returned(loan_id)
    
    async def mark_as_returned(self, loan_id: uuid.UUID) -> Optional[Loan]:
        loan = await self.get(loan_id)
        if not loan:
            return None
        
        loan.status = "returned"
        loan.return_date = datetime.now(timezone.utc)
        loan.updated_at = datetime.now(timezone.utc)
        await self._db.commit()
        await self._db.refresh(loan)
        return loan
    
    async def mark_as_overdue(self, loan_id: uuid.UUID) -> Optional[Loan]:
        loan = await self.get(loan_id)
        if not loan:
            return None
        
        loan.status = "overdue"
        loan.updated_at = datetime.now(timezone.utc)
        await self._db.commit()
        await self._db.refresh(loan)
        return loan
    
    async def get_overdue_loans(self, check_date: Optional[datetime] = None,) -> List[Loan]:
        if check_date is None:
            check_date = datetime.now(timezone.utc)
        result = await self._db.execute(select(Loan).where(and_(Loan.status == "active", Loan.due_date < check_date)))
        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Loan))
        return result.scalar() or 0
    
    async def count_active(self) -> int:
        result = await self._db.execute(select(func.count()).where(Loan.status == "active"))
        return result.scalar() or 0
    
    async def get_daily_stats(self, days: int = 30) -> List[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(func.date(Loan.created_at).label("date"), func.count().label("count"))
            .where(Loan.created_at >= since)
            .group_by(func.date(Loan.created_at))
            .order_by(func.date(Loan.created_at))
        )
        result = await self._db.execute(stmt)
        return [{"date": str(row.date), "count": row.count} for row in result.all()]
    
    async def get_average_duration(self, days: int = 30) -> float:
        return 14.0
    
    async def count_loans(self) -> int:
        return await self.count_all()
    
    async def get_multi_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        borrower_id: Optional[uuid.UUID] = None,
        lender_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[Loan], int]:
        query = select(Loan)
        
        if status:
            query = query.where(Loan.status == status)
        if borrower_id:
            query = query.where(Loan.borrower_id == borrower_id)
        if lender_id:
            query = query.where(Loan.lender_id == lender_id)
    
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self._db.execute(count_query)).scalar() or 0
        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all()), total
