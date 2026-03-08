import logging
from uuid import UUID
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from database.interfaces import (
    ILoanRequestRepository,
    ILoanRepository,
    IUserBookRepository,
    IMessageRepository
)
from src.services.interfaces.loans import ILoanRequestService
from src.core.exceptions import (
    BookNotFoundException,
    NotAuthorizedException,
    LoanRequestNotFoundException,
    DuplicateLoanRequestException,
)
from src.schemas.loan import LoanRequestResponse

from .message_handler import LoanRequestMessageHandler
from .status_manager import LoanRequestStatusManager

logger = logging.getLogger(__name__)


class LoanRequestService(ILoanRequestService):
    def __init__(
        self,
        request_repo: ILoanRequestRepository,
        loan_repo: ILoanRepository,
        user_book_repo: IUserBookRepository,
        message_repo: Optional[IMessageRepository] = None,
        db: Optional[AsyncSession] = None
    ):
        self._request_repo = request_repo
        self._loan_repo = loan_repo
        self._user_book_repo = user_book_repo
        self._message_repo = message_repo
        self._db = db
        self._message_handler = LoanRequestMessageHandler(message_repo)
        self._status_manager = LoanRequestStatusManager(
            request_repo=request_repo,
            loan_repo=loan_repo,
            user_book_repo=user_book_repo,
            message_handler=self._message_handler,
            db=db
        )
    
    async def create_request(self, user_book_id: UUID, requester_id: UUID, message: Optional[str] = None) -> LoanRequestResponse:
        user_book = await self._user_book_repo.get_by_id_for_update(user_book_id)
        if not user_book:
            raise BookNotFoundException(user_book_id)
        if user_book.status != "available":
            raise ValueError("Book copy is not available")
        if not user_book.is_lendable:
            raise ValueError("This book copy is not available for lending")
        if user_book.user_id == requester_id:
            raise ValueError("Cannot borrow your own book")
        has_pending = await self._request_repo.has_pending_request(user_book_id, requester_id)
        if has_pending:
            raise DuplicateLoanRequestException()
        try:
            request = await self._request_repo.create(
                user_book_id=user_book_id,
                requester_id=requester_id,
                owner_id=user_book.user_id,
                message=message
            )
        except IntegrityError:
            raise DuplicateLoanRequestException()
        await self._message_handler.notify_request_created(request.id)
        if message and self._message_repo:
            await self._message_repo.create(loan_request_id=request.id, sender_id=requester_id, content=message, message_type="text")
        
        logger.info(f"Loan request created: {request.id} for book {user_book_id} by user {requester_id}")
        return self._to_response(request)
    
    async def reserve_request(self, request_id: UUID, owner_id: UUID) -> LoanRequestResponse:
        await self._status_manager.reserve(request_id, owner_id)
        request = await self._request_repo.get_by_id(request_id)
        return self._to_response(request)
    
    async def accept_request(self, request_id: UUID, owner_id: UUID) -> LoanRequestResponse:
        await self._status_manager.accept(request_id, owner_id)
        request = await self._request_repo.get_by_id(request_id)
        return self._to_response(request)
    
    async def reject_request(self, request_id: UUID, owner_id: UUID, reason: Optional[str] = None) -> LoanRequestResponse:
        await self._status_manager.reject(request_id, owner_id, reason)
        request = await self._request_repo.get_by_id(request_id)
        return self._to_response(request)
    
    async def cancel_request(self, request_id: UUID, requester_id: UUID) -> bool:
        await self._status_manager.cancel(request_id, requester_id)
        return True
    
    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = "pending", skip: int = 0, limit: int = 100) -> Tuple[List[LoanRequestResponse], int]:
        requests, total = await self._request_repo.get_incoming_requests(owner_id, status, skip, limit)
        return [self._to_response(r) for r in requests], total
    
    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> Tuple[List[LoanRequestResponse], int]:
        requests, total = await self._request_repo.get_outgoing_requests(requester_id, status, skip, limit)
        return [self._to_response(r) for r in requests], total
    
    async def get_by_id(self, request_id: UUID) -> Optional[LoanRequestResponse]:
        request = await self._request_repo.get_by_id(request_id)
        if not request:
            return None
        return self._to_response(request)
    
    async def update(self, request_id: UUID, data: dict) -> LoanRequestResponse:
        updated = await self._request_repo.partial_update(request_id, data)
        if not updated:
            request = await self._request_repo.get_by_id(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            raise ValueError("Failed to update request")
        logger.info(f"Updated request: {request_id}")
        return self._to_response(updated)
    
    async def get_summary(self, user_id: UUID) -> dict:
        incoming_pending = await self._request_repo.count_pending_for_owner(user_id)
        outgoing_pending = await self._request_repo.count_pending_for_requester(user_id)
        return {
            "incoming_pending": incoming_pending,
            "outgoing_pending": outgoing_pending,
        }
    
    def _to_response(self, request) -> LoanRequestResponse:
        user_book = request.user_book
        book = user_book.book if user_book else None
        owner = request.owner
        requester = request.requester
        cover_url = None
        if book and book.isbn:
            cover_url = f"/covers/{book.isbn}.jpg"
        
        return LoanRequestResponse(
            id=request.id,
            user_book_id=request.user_book_id,
            book_id=book.id if book else None,
            book_title=book.title if book else "Unknown",
            book_cover_url=cover_url,
            owner_id=request.owner_id,
            owner_name=f"{owner.first_name} {owner.last_name}" if owner else "Unknown",
            owner_avatar=owner.avatar_url if owner else None,
            requester_id=request.requester_id,
            requester_name=f"{requester.first_name} {requester.last_name}" if requester else "Unknown",
            requester_avatar=requester.avatar_url if requester else None,
            status=request.status,
            message=request.message,
            rejection_reason=request.rejection_reason,
            created_at=request.created_at,
            responded_at=request.responded_at
        )
