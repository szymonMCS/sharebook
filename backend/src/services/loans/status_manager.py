import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import ILoanRequestRepository, ILoanRepository, IUserBookRepository
from src.core.exceptions import (
    LoanRequestNotFoundException,
    NotAuthorizedException,
    InvalidLoanRequestStatusException,
    BookNotFoundException,
)
from src.core.constants import LOAN_DURATION_DAYS, MAX_ACTIVE_LOANS
from .message_handler import LoanRequestMessageHandler

logger = logging.getLogger(__name__)


class LoanRequestStatusManager:
    def __init__(
        self,
        request_repo: ILoanRequestRepository,
        loan_repo: ILoanRepository,
        user_book_repo: IUserBookRepository,
        message_handler: LoanRequestMessageHandler,
        db: AsyncSession
    ):
        self._request_repo = request_repo
        self._loan_repo = loan_repo
        self._user_book_repo = user_book_repo
        self._message_handler = message_handler
        self._db = db
    
    async def accept(self, request_id: UUID, owner_id: UUID) -> datetime:
        async with self._db.begin():
            request = await self._request_repo.get_by_id_for_update(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            if request.owner_id != owner_id:
                raise NotAuthorizedException("You are not the owner of this request")
            if request.status not in ["pending", "reserved"]:
                raise InvalidLoanRequestStatusException(f"Cannot accept request with status: {request.status}")
            active_count = await self._loan_repo.count_active_for_borrower(request.requester_id)
            if active_count >= MAX_ACTIVE_LOANS:
                raise ValueError(f"Borrower has reached maximum {MAX_ACTIVE_LOANS} active loans")
            user_book = await self._user_book_repo.get_by_id_for_update(request.user_book_id)
            if not user_book:
                raise BookNotFoundException(request.user_book_id)
            due_date = datetime.now(timezone.utc) + timedelta(days=LOAN_DURATION_DAYS)
            loan = await self._loan_repo.create(
                user_book_id=request.user_book_id,
                borrower_id=request.requester_id,
                lender_id=owner_id,
                loan_duration_days=LOAN_DURATION_DAYS
            )
            await self._user_book_repo.update_status(request.user_book_id, "borrowed")
            await self._request_repo.update_status(request_id, "accepted")
            await self._reject_other_requests(request_id, request.user_book_id, owner_id)
            logger.info(f"Loan request accepted: {request_id} by owner {owner_id}, loan {loan.id}")
        await self._message_handler.notify_accepted(request_id, due_date.strftime('%d.%m.%Y'))
        return due_date
    
    async def reserve(self, request_id: UUID, owner_id: UUID) -> None:
        async with self._db.begin():
            request = await self._request_repo.get_by_id_for_update(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            if request.owner_id != owner_id:
                raise NotAuthorizedException("You are not the owner of this request")
            if request.status != "pending":
                raise InvalidLoanRequestStatusException("Request is not in pending status")
            await self._request_repo.update_status(request_id, "reserved")
            await self._user_book_repo.update_status(request.user_book_id, "reserved")
            logger.info(f"Loan request reserved: {request_id} by owner {owner_id}")
        await self._message_handler.notify_reserved(request_id)
    
    async def reject(self, request_id: UUID, owner_id: UUID, reason: Optional[str] = None) -> None:
        async with self._db.begin():
            request = await self._request_repo.get_by_id_for_update(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            if request.owner_id != owner_id:
                raise NotAuthorizedException("You are not the owner of this request")
            if request.status not in ["pending", "reserved"]:
                raise InvalidLoanRequestStatusException(f"Cannot reject request with status: {request.status}")
            await self._request_repo.update_status(request_id, "rejected", rejection_reason=reason)
            await self._maybe_set_available(request.user_book_id)
            logger.info(f"Loan request rejected: {request_id} by owner {owner_id}")
        await self._message_handler.notify_rejected(request_id, reason)
    
    async def cancel(self, request_id: UUID, borrower_id: UUID) -> None:
        async with self._db.begin():
            request = await self._request_repo.get_by_id_for_update(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            if request.requester_id != borrower_id:
                raise NotAuthorizedException("You are not the author of this request")
            if request.status != "pending":
                raise InvalidLoanRequestStatusException("Only pending requests can be cancelled")
            user_book_id = request.user_book_id
            await self._request_repo.delete(request_id)
            await self._maybe_set_available(user_book_id)
            logger.info(f"Loan request cancelled: {request_id} by borrower {borrower_id}")
        await self._message_handler.notify_cancelled(request_id)
    
    async def _reject_other_requests(self, accepted_request_id: UUID, user_book_id: UUID, owner_id: UUID) -> None:
        other_requests = await self._request_repo.get_pending_for_book(user_book_id)
        for other in other_requests:
            if other.id != accepted_request_id:
                await self._request_repo.update_status(other.id, "rejected", rejection_reason="Książka została wypożyczona innej osobie")
                await self._message_handler.notify_auto_rejected(other.id, "Książka została wypożyczona innej osobie.")
                logger.info(f"Auto-rejected request {other.id} as book was loaned to another user")
    
    async def _maybe_set_available(self, user_book_id: UUID) -> None:
        pending_count = await self._request_repo.count_pending_for_book(user_book_id)
        reserved_count = await self._request_repo.count_reserved_for_book(user_book_id)
        if pending_count == 0 and reserved_count == 0:
            await self._user_book_repo.update_status(user_book_id, "available")
            logger.info(f"Book {user_book_id} set back to available")
