import uuid
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.models import Message, LoanRequest, User
from database.interfaces import IMessageRepository


class MessageRepository(IMessageRepository): 
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def get_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        result = await self._db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()
    
    async def create(self, loan_request_id: uuid.UUID, sender_id: uuid.UUID, content: str, message_type: str = "text",) -> Message:
        message = Message(
            loan_request_id=loan_request_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            is_read=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._db.add(message)
        await self._db.commit()
        await self._db.refresh(message)
        return message
    
    async def mark_as_read(self, message_id: uuid.UUID) -> Optional[Message]:
        message = await self.get_by_id(message_id)
        if not message:
            return None
        
        message.is_read = True
        message.updated_at = datetime.now(timezone.utc)
        
        await self._db.commit()
        await self._db.refresh(message)
        return message
    
    async def mark_all_as_read_for_request(self, loan_request_id: uuid.UUID, user_id: uuid.UUID,) -> int:
        result = await self._db.execute(select(Message).where(Message.loan_request_id == loan_request_id, Message.sender_id != user_id, Message.is_read == False))
        messages = result.scalars().all()
        
        count = 0
        for message in messages:
            message.is_read = True
            message.updated_at = datetime.now(timezone.utc)
            count += 1
        if count > 0:
            await self._db.commit()
        return count
    
    async def get_by_loan_request(self, loan_request_id: uuid.UUID, skip: int = 0, limit: int = 100, include_sender: bool = False,) -> List[Message]:
        stmt = select(Message).where(Message.loan_request_id == loan_request_id)
        if include_sender:
            stmt = stmt.options(joinedload(Message.sender))
        stmt = stmt.order_by(Message.created_at.asc()).offset(skip).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_unread_messages_for_user(self, user_id: uuid.UUID,) -> List[Message]:
        result = await self._db.execute(
            select(Message)
            .join(LoanRequest, Message.loan_request_id == LoanRequest.id)
            .where(
                Message.is_read == False,
                Message.sender_id != user_id,
                Message.message_type == "text",
                ((LoanRequest.owner_id == user_id) | (LoanRequest.requester_id == user_id))
            )
            .order_by(Message.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def count_unread_for_user(self, user_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .join(LoanRequest, Message.loan_request_id == LoanRequest.id)
            .where(
                Message.is_read == False,
                Message.sender_id != user_id,
                ((LoanRequest.owner_id == user_id) | (LoanRequest.requester_id == user_id))
            )
        )
        return result.scalar()
    
    async def count_messages_for_request(self, loan_request_id: uuid.UUID) -> int:
        result = await self._db.execute(select(func.count()).where(Message.loan_request_id == loan_request_id))
        return result.scalar()
    
    async def mark_all_as_read(self, loan_request_id: uuid.UUID, user_id: uuid.UUID) -> int:
        return await self.mark_all_as_read_for_request(loan_request_id, user_id)
    
    async def get_unread_count(self, loan_request_id: uuid.UUID, user_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .where(
                Message.loan_request_id == loan_request_id,
                Message.is_read == False,
                Message.sender_id != user_id
            )
        )
        return result.scalar() or 0
    
    async def create_system_message(self, loan_request_id: uuid.UUID, content: str) -> Message:
        message = Message(
            loan_request_id=loan_request_id,
            sender_id=None,
            content=content,
            message_type="system",
            is_read=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._db.add(message)
        await self._db.commit()
        await self._db.refresh(message)
        return message
