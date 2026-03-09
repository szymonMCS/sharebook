from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import ILoanRequestRepository
from database.models import LoanRequest

class LoanRequestRepository(ILoanRequestRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, request_id: UUID) -> Optional[LoanRequest]:
        result = await self._db.execute(select(LoanRequest).where(LoanRequest.id == request_id))
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

    async def update_status(self, request_id: UUID, status: str, rejection_reason: Optional[str] = None, commit: bool = True) -> Optional[LoanRequest]:
        request = await self.get_by_id(request_id)
        if not request:
            return None

        request.status = status
        if rejection_reason and status == "rejected":
            request.rejection_reason = rejection_reason
        request.updated_at = datetime.now(timezone.utc)

        if commit:
            await self._db.commit()
            await self._db.refresh(request)
        else:
            await self._db.flush()
            await self._db.refresh(request)
        return request

    async def _get_requests_base(
        self,
        filter_column,
        filter_value: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[LoanRequest], int]:
        count_query = select(func.count()).where(filter_column == filter_value)
        if status:
            count_query = count_query.where(LoanRequest.status == status)
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0
        
        query = select(LoanRequest).where(filter_column == filter_value)
        if status:
            query = query.where(LoanRequest.status == status)
        query = query.order_by(LoanRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all()), total

    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List[LoanRequest], int]:
        return await self._get_requests_base(LoanRequest.owner_id, owner_id, status, skip, limit)

    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List[LoanRequest], int]:
        return await self._get_requests_base(LoanRequest.requester_id, requester_id, status, skip, limit)

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

    async def get_by_id_for_update(self, request_id: UUID) -> Optional[LoanRequest]:
        result = await self._db.execute(select(LoanRequest).where(LoanRequest.id == request_id).with_for_update())
        return result.scalar_one_or_none()

    async def update_status_atomic(
        self, 
        request_id: UUID, 
        status: str, 
        expected_status: str,
        owner_id: Optional[UUID] = None,
        requester_id: Optional[UUID] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[LoanRequest]:
        update_values = {
            "status": status,
            "updated_at": datetime.now(timezone.utc)
        }
        if rejection_reason:
            update_values["rejection_reason"] = rejection_reason
        
        where_clause = [
            LoanRequest.id == request_id,
            LoanRequest.status == expected_status
        ]
        if owner_id:
            where_clause.append(LoanRequest.owner_id == owner_id)
        if requester_id:
            where_clause.append(LoanRequest.requester_id == requester_id)
        
        result = await self._db.execute(update(LoanRequest).where(and_(*where_clause)).values(**update_values))
        await self._db.commit()
        
        if result.rowcount == 0:
            return None
        
        return await self.get_by_id(request_id)

    async def partial_update(self, request_id: UUID, data: dict) -> Optional[LoanRequest]:
        update_values = {"updated_at": datetime.now(timezone.utc)}
        if "message" in data and data["message"] is not None:
            update_values["message"] = data["message"]
        
        result = await self._db.execute(update(LoanRequest).where(LoanRequest.id == request_id).values(**update_values))
        await self._db.commit()
        
        if result.rowcount == 0:
            return None
        
        return await self.get_by_id(request_id)

    async def count_pending_for_book(self, user_book_id: UUID) -> int:
        result = await self._db.execute(select(func.count()).where(and_(LoanRequest.user_book_id == user_book_id, LoanRequest.status == "pending"))
)
        return result.scalar() or 0

    async def count_reserved_for_book(self, user_book_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .where(
                and_(
                    LoanRequest.user_book_id == user_book_id,
                    LoanRequest.status == "reserved"
                )
            )
        )
        return result.scalar() or 0

    async def get_pending_for_book(self, user_book_id: UUID) -> List[LoanRequest]:
        result = await self._db.execute(
            select(LoanRequest)
            .where(
                and_(
                    LoanRequest.user_book_id == user_book_id,
                    LoanRequest.status == "pending"
                )
            )
        )
        return list(result.scalars().all())

    async def delete(self, request_id: UUID) -> bool:
        request = await self.get_by_id(request_id)
        if not request:
            return False
        
        await self._db.delete(request)
        await self._db.commit()
        return True
