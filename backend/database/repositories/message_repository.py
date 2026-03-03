from uuid import UUID
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import IMessageRepository
from database.models import Message, LoanRequest


class MessageRepository(IMessageRepository):
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def create(self, loan_request_id: UUID, sender_id: UUID, content: str, message_type: str = "text") -> Message:
        message = Message(
            loan_request_id=loan_request_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            is_read=False
        )
        self._db.add(message)
        await self._db.commit()
        await self._db.refresh(message)
        return message
    
    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        result = await self._db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()
    
    async def get_by_loan_request(self, loan_request_id: UUID, include_sender: bool = True) -> List[Message]:
        query = select(Message).where(Message.loan_request_id == loan_request_id).order_by(Message.created_at.asc())
        
        if include_sender:
            query = query.options(joinedload(Message.sender))
        
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_unread_count(self, loan_request_id: UUID, user_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count(Message.id)).where(
                and_(
                    Message.loan_request_id == loan_request_id,
                    Message.sender_id != user_id,  # Nie liczymy własnych wiadomości
                    Message.is_read == False
                )
            )
        )
        return result.scalar() or 0
    
    async def mark_as_read(self, message_id: UUID) -> bool:
        message = await self.get_by_id(message_id)
        if not message:
            return False
        
        message.is_read = True
        await self._db.commit()
        return True
    
    async def mark_all_as_read(self, loan_request_id: UUID, user_id: UUID) -> int:
        result = await self._db.execute(
            select(Message).where(
                and_(
                    Message.loan_request_id == loan_request_id,
                    Message.sender_id != user_id,
                    Message.is_read == False
                )
            )
        )
        messages = result.scalars().all()
        
        count = 0
        for msg in messages:
            msg.is_read = True
            count += 1
        
        if count > 0:
            await self._db.commit()
        
        return count
    
    async def create_system_message(self, loan_request_id: UUID, content: str) -> Message:
        # Pobierz prośbę aby uzyskać owner_id
        result = await self._db.execute(select(LoanRequest).where(LoanRequest.id == loan_request_id))
        loan_request = result.scalar_one_or_none()
        
        if not loan_request:
            raise ValueError(f"Loan request {loan_request_id} not found")
        
        # System message jest wysyłana w imieniu ownera
        return await self.create(
            loan_request_id=loan_request_id,
            sender_id=loan_request.owner_id,
            content=content,
            message_type="system"
        )
