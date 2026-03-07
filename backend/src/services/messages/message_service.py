import logging
from uuid import UUID
from typing import Optional
from database.interfaces import IMessageRepository, ILoanRequestRepository, IUserBookRepository
from src.services.interfaces.messages import IMessageService
from src.schemas.loan import MessageResponse, MessageThreadResponse
from src.core.exceptions import NotAuthorizedException, LoanRequestNotFoundException

logger = logging.getLogger(__name__)


class MessageService(IMessageService):
    def __init__(
        self,
        message_repo: IMessageRepository,
        request_repo: ILoanRequestRepository,
        user_book_repo: Optional[IUserBookRepository] = None
    ):
        self._message_repo = message_repo
        self._request_repo = request_repo
        self._user_book_repo = user_book_repo
    
    async def send_message(self, loan_request_id: UUID, sender_id: UUID, content: str) -> MessageResponse:
        request = await self._request_repo.get_by_id(loan_request_id)
        if not request:
            raise LoanRequestNotFoundException(loan_request_id)
        
        if sender_id not in [request.requester_id, request.owner_id]:
            raise NotAuthorizedException(
                "You are not part of this conversation"
            )
        
        message = await self._message_repo.create(
            loan_request_id=loan_request_id,
            sender_id=sender_id,
            content=content,
            message_type="text"
        )
        
        logger.info(f"Message sent in request {loan_request_id} by user {sender_id}")
        return self._to_response(message)
    
    async def get_thread(self, loan_request_id: UUID, user_id: UUID) -> MessageThreadResponse:
        request = await self._request_repo.get_by_id(loan_request_id)
        if not request:
            raise LoanRequestNotFoundException(loan_request_id)
        
        if user_id not in [request.requester_id, request.owner_id]:
            raise NotAuthorizedException("You are not part of this conversation")
        
        messages = await self._message_repo.get_by_loan_request(loan_request_id, include_sender=True)
        
        unread_count = await self._message_repo.get_unread_count(loan_request_id, user_id)
        
        book_title = "Unknown Book"
        if self._user_book_repo:
            try:
                user_book = await self._user_book_repo.get_by_id(request.user_book_id)
                if user_book and user_book.book:
                    book_title = user_book.book.title
            except Exception as e:
                logger.warning(f"Could not fetch book title for request {request.id}: {e}")
        
        message_responses = [self._to_response(m) for m in messages]
        
        return MessageThreadResponse(
            loan_request_id=loan_request_id,
            user_book_id=request.user_book_id,
            book_title=book_title,
            status=request.status,
            messages=message_responses,
            total_messages=len(message_responses),
            unread_count=unread_count
        )
    
    async def mark_message_as_read(self, message_id: UUID, user_id: UUID) -> bool:
        message = await self._message_repo.get_by_id(message_id)
        if not message:
            raise LoanRequestNotFoundException(message_id)
        
        if message.sender_id == user_id:
            return False
        
        request = await self._request_repo.get_by_id(message.loan_request_id)
        if not request or user_id not in [request.requester_id, request.owner_id]:
            raise NotAuthorizedException()
        
        return await self._message_repo.mark_as_read(message_id)
    
    async def mark_all_as_read(self, loan_request_id: UUID, user_id: UUID) -> int:
        request = await self._request_repo.get_by_id(loan_request_id)
        if not request or user_id not in [request.requester_id, request.owner_id]:
            raise NotAuthorizedException()
        
        return await self._message_repo.mark_all_as_read(loan_request_id, user_id)
    
    async def add_system_message(self, loan_request_id: UUID, content: str) -> MessageResponse:
        message = await self._message_repo.create_system_message(
            loan_request_id=loan_request_id,
            content=content
        )
        logger.info(f"System message added to request {loan_request_id}: {content[:50]}...")
        return self._to_response(message)
    
    def _to_response(self, message) -> MessageResponse:
        sender_name = "Unknown"
        sender_avatar = None
        
        if hasattr(message, 'sender') and message.sender:
            first_name = message.sender.first_name or ""
            last_name = message.sender.last_name or ""
            sender_name = f"{first_name} {last_name}".strip() or "Unknown"
        
        return MessageResponse(
            id=message.id,
            loan_request_id=message.loan_request_id,
            sender_id=message.sender_id,
            sender_name=sender_name,
            sender_avatar=sender_avatar,
            content=message.content,
            message_type=message.message_type,
            is_read=message.is_read,
            created_at=message.created_at
        )
