import uuid
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.models import LoanRequest, UserBook
from database.interfaces import ILoanRequestRepository


class LoanRequestRepository(ILoanRequestRepository):
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def get_by_id(self, request_id: uuid.UUID) -> Optional[LoanRequest]:
        result = await self._db.execute(select(LoanRequest).where(LoanRequest.id == request_id))
        return result.scalar_one_or_none()
    
    async def get_by_id_with_relations(self, request_id: uuid.UUID,) -> Optional[LoanRequest]:
        result = await self._db.execute(
            select(LoanRequest)
            .options(
                joinedload(LoanRequest.requester),
                joinedload(LoanRequest.owner),
                joinedload(LoanRequest.user_book).joinedload(UserBook.book)
            )
            .where(LoanRequest.id == request_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_book_id: uuid.UUID, requester_id: uuid.UUID, owner_id: uuid.UUID, message: Optional[str] = None) -> LoanRequest:
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
    
    async def update_status(self, request_id: uuid.UUID, status: str, rejection_reason: Optional[str] = None,) -> Optional[LoanRequest]:
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
    
    async def delete(self, request_id: uuid.UUID) -> bool:
        request = await self.get_by_id(request_id)
        if not request:
            return False
        await self._db.delete(request)
        await self._db.commit()
        return True
    
    async def get_incoming_requests(self, owner_id: uuid.UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100,) -> tuple[List[LoanRequest], int]:
        count_query = select(func.count()).where(LoanRequest.owner_id == owner_id)
        if status:
            count_query = count_query.where(LoanRequest.status == status)
        total_result = await self._db.execute(count_query)
        total = total_result.scalar()
        
        query = select(LoanRequest).where(LoanRequest.owner_id == owner_id)
        if status:
            query = query.where(LoanRequest.status == status)
        query = query.order_by(LoanRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all()), total
    
    async def get_outgoing_requests(self, requester_id: uuid.UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100,) -> tuple[List[LoanRequest], int]:
        count_query = select(func.count()).where(LoanRequest.requester_id == requester_id)
        if status:
            count_query = count_query.where(LoanRequest.status == status)
        total_result = await self._db.execute(count_query)
        total = total_result.scalar()
        
        query = select(LoanRequest).where(LoanRequest.requester_id == requester_id)
        if status:
            query = query.where(LoanRequest.status == status)
        query = query.order_by(LoanRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all()), total
    
    async def get_requests_for_user_book(self, user_book_id: uuid.UUID, status: Optional[str] = None,) -> List[LoanRequest]:
        query = select(LoanRequest).where(LoanRequest.user_book_id == user_book_id)
        if status:
            query = query.where(LoanRequest.status == status)
        query = query.order_by(LoanRequest.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def has_pending_request(self, user_book_id: uuid.UUID, requester_id: uuid.UUID,) -> bool:
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
    
    async def count_incoming_pending(self, owner_id: uuid.UUID) -> int:
        result = await self._db.execute(select(func.count()).where(and_(LoanRequest.owner_id == owner_id, LoanRequest.status == "pending")))
        return result.scalar()
    
    async def count_outgoing_pending(self, requester_id: uuid.UUID) -> int:
        result = await self._db.execute(select(func.count()).where(and_(LoanRequest.requester_id == requester_id, LoanRequest.status == "pending")))
        return result.scalar()
    
    async def get_by_id_for_update(self, request_id: uuid.UUID) -> Optional[LoanRequest]:
        result = await self._db.execute(select(LoanRequest).where(LoanRequest.id == request_id).with_for_update())
        return result.scalar_one_or_none()
    
    async def partial_update(self, request_id: uuid.UUID, data: dict) -> Optional[LoanRequest]:
        request = await self.get_by_id(request_id)
        if not request:
            return None
        for field, value in data.items():
            if hasattr(request, field):
                setattr(request, field, value)
        request.updated_at = datetime.now(timezone.utc)
        await self._db.commit()
        await self._db.refresh(request)
        return request
    
    async def get_pending_for_book(self, user_book_id: uuid.UUID) -> List[LoanRequest]:
        return await self.get_requests_for_user_book(user_book_id, status="pending")
    
    async def count_pending_for_book(self, user_book_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count()).where(and_(LoanRequest.user_book_id == user_book_id, LoanRequest.status == "pending")))
        return result.scalar() or 0
    
    async def count_reserved_for_book(self, user_book_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count()).where(and_(LoanRequest.user_book_id == user_book_id, LoanRequest.status == "reserved")))
        return result.scalar() or 0
    
    async def count_pending_for_owner(self, user_id: uuid.UUID) -> int:
        return await self.count_incoming_pending(user_id)
    
    async def count_pending_for_requester(self, user_id: uuid.UUID) -> int:
        return await self.count_outgoing_pending(user_id)
