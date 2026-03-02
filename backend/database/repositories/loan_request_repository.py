from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.interfaces import ILoanRequestRepository
from database.models import LoanRequest


class LoanRequestRepository(ILoanRequestRepository):

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, request_id: UUID) -> Optional[LoanRequest]:
        result = await self._db.execute(
            select(LoanRequest).where(LoanRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_book_id: UUID, requester_id: UUID, owner_id: UUID, message: Optional[str] = None) -> LoanRequest:
        request = LoanRequest(
            user_book_id=user_book_id,
            requester_id=requester_id,
            owner_id=owner_id,
            status="pending",
            message=message,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._db.add(request)
        await self._db.commit()
        await self._db.refresh(request)
        return request

    async def update_status(self, request_id: UUID, status: str, rejection_reason: Optional[str] = None) -> Optional[LoanRequest]:
        request = await self.get_by_id(request_id)
        if not request:
            return None

        request.status = status
        if rejection_reason and status == "rejected":
            request.rejection_reason = rejection_reason
        request.updated_at = datetime.now(timezone.utc)

        await self._db.commit()
        await self._db.refresh(request)
        return request

    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = None) -> List[LoanRequest]:
        query = select(LoanRequest).where(LoanRequest.owner_id == owner_id)
        if status:
            query = query.where(LoanRequest.status == status)
        query = query.order_by(LoanRequest.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None) -> List[LoanRequest]:
        query = select(LoanRequest).where(LoanRequest.requester_id == requester_id)
        if status:
            query = query.where(LoanRequest.status == status)
        query = query.order_by(LoanRequest.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def has_pending_request(self, user_book_id: UUID, requester_id: UUID) -> bool:
        result = await self._db.execute(
            select(func.count())
            .where(
                and_(
                    LoanRequest.user_book_id == user_book_id,
                    LoanRequest.requester_id == requester_id,
                    LoanRequest.status == "pending"
                )
            )
        )
        return result.scalar() > 0

    async def count_pending_for_owner(self, owner_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .where(
                and_(
                    LoanRequest.owner_id == owner_id,
                    LoanRequest.status == "pending"
                )
            )
        )
        return result.scalar() or 0

    async def count_pending_for_requester(self, requester_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .where(
                and_(
                    LoanRequest.requester_id == requester_id,
                    LoanRequest.status == "pending"
                )
            )
        )
        return result.scalar() or 0
