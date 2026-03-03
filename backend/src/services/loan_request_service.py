import logging
from typing import Optional, List
from uuid import UUID
from database.interfaces import (
    ILoanRequestRepository,
    ILoanRepository,
    IUserBookRepository,
)
from src.services.interfaces import ILoanRequestService, IMessageService
from src.core.constants import MAX_ACTIVE_LOANS
from src.core.exceptions import (
    BookNotFoundException,
    NotAuthorizedException,
    LoanRequestNotFoundException
)
from database.models import LoanRequest

logger = logging.getLogger(__name__)


class LoanRequestService(ILoanRequestService):
    def __init__(
        self,
        request_repo: ILoanRequestRepository,
        loan_repo: ILoanRepository,
        user_book_repo: IUserBookRepository,
        message_service: Optional[IMessageService] = None 
    ):
        self._request_repo = request_repo
        self._loan_repo = loan_repo
        self._user_book_repo = user_book_repo
        self._message_service = message_service

    async def create_request(self, user_book_id: UUID, requester_id: UUID, message: Optional[str] = None) -> LoanRequest:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        if not user_book:
            raise BookNotFoundException(user_book_id)

        if user_book.status != "available":
            raise ValueError("Book copy is not available")

        if not user_book.is_lendable:
            raise ValueError("This book copy is not available for lending")

        if user_book.user_id == requester_id:
            raise ValueError("Cannot borrow your own book")

        owner_id = user_book.user_id

        has_pending = await self._request_repo.has_pending_request(user_book_id, requester_id)
        if has_pending:
            raise ValueError("You already have a pending request for this book copy")

        request = await self._request_repo.create(
            user_book_id=user_book_id,
            requester_id=requester_id,
            owner_id=owner_id,
            message=message,
        )
        
        if self._message_service:
            try:
                await self._message_service.add_system_message(
                    request.id,
                    "Prośba o wypożyczenie została utworzona."
                )
            except Exception as e:
                logger.warning(f"Failed to create system message: {e}")

        logger.info(f"Created request: {request.id}")
        return request

    async def accept_request(self, request_id: UUID, owner_id: UUID) -> LoanRequest:
        request = await self._request_repo.get_by_id(request_id)
        if not request:
            raise LoanRequestNotFoundException(request_id)

        if request.owner_id != owner_id:
            raise NotAuthorizedException("You are not the owner of this request")

        if request.status != "pending":
            raise ValueError(f"Cannot accept - current status: {request.status}")

        updated_request = await self._request_repo.update_status(request_id, "accepted")
        
        logger.info(f"Accepted request: {request_id}")
        return updated_request

    async def reject_request(self, request_id: UUID, owner_id: UUID, reason: Optional[str] = None) -> LoanRequest:
        request = await self._request_repo.get_by_id(request_id)
        if not request:
            raise LoanRequestNotFoundException(request_id)

        if request.owner_id != owner_id:
            raise NotAuthorizedException("You are not the owner of this request")

        if request.status != "pending":
            raise ValueError(f"Cannot reject - current status: {request.status}")

        updated_request = await self._request_repo.update_status(request_id, "rejected", reason)
        
        if self._message_service:
            try:
                content = "Właściciel odrzucił prośbę o wypożyczenie."
                if reason:
                    content += f" Powód: {reason}"
                await self._message_service.add_system_message(request_id, content)
            except Exception as e:
                logger.warning(f"Failed to create system message: {e}")

        logger.info(f"Rejected request: {request_id}")
        return updated_request

    async def cancel_request(self, request_id: UUID, requester_id: UUID) -> bool:
        request = await self._request_repo.get_by_id(request_id)
        if not request:
            raise LoanRequestNotFoundException(request_id)

        if request.requester_id != requester_id:
            raise NotAuthorizedException("You are not the author of this request")

        if request.status != "pending":
            raise ValueError(f"Cannot cancel - current status: {request.status}")

        await self._request_repo.update_status(request_id, "cancelled")
        
        if self._message_service:
            try:
                await self._message_service.add_system_message(
                    request_id,
                    "Prośba o wypożyczenie została anulowana przez proszącego."
                )
            except Exception as e:
                logger.warning(f"Failed to create system message: {e}")

        logger.info(f"Cancelled request: {request_id}")
        return True

    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = "pending") -> List[LoanRequest]:
        requests = await self._request_repo.get_incoming_requests(owner_id, status)
        return requests

    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None) -> List[LoanRequest]:
        requests = await self._request_repo.get_outgoing_requests(requester_id, status)
        return requests

    async def get_request_details(self, request_id: UUID) -> Optional[LoanRequest]:
        request = await self._request_repo.get_by_id(request_id)
        if not request:
            return None
        return request

    async def get_summary(self, user_id: UUID) -> dict:
        incoming_pending = await self._request_repo.count_pending_for_owner(user_id)
        outgoing_pending = await self._request_repo.count_pending_for_requester(user_id)

        return {
            "incoming_pending": incoming_pending,
            "outgoing_pending": outgoing_pending,
        }
