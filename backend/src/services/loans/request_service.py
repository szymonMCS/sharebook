import logging
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from database.interfaces import (
    ILoanRequestRepository,
    ILoanRepository,
    IUserBookRepository,
)
from src.services.interfaces.loans import ILoanRequestService
from src.services.interfaces.messages import IMessageService
from src.core.exceptions import (
    BookNotFoundException,
    NotAuthorizedException,
    LoanRequestNotFoundException
)
from database.models import LoanRequest

logger = logging.getLogger(__name__)


async def _publish_system_message_event(
    event_type: str,
    request_id: UUID,
    content: str,
    message_service: Optional[IMessageService] = None,
    use_outbox: bool = True
) -> None:
    try:
        from src.events import get_event_bus, DomainEvent
        event_bus = get_event_bus()
        
        event_bus.publish_sync(DomainEvent(
            event_type=event_type,
            payload={"content": content},
            occurred_at=datetime.now(timezone.utc),
            entity_id=request_id
        ))
        logger.debug(f"Published event {event_type} for request {request_id}")
        
    except Exception as e:
        logger.warning(f"EventBus failed, using direct message_service: {e}")
        
        if message_service:
            try:
                await message_service.add_system_message(request_id, content)
            except Exception as msg_err:
                logger.warning(f"Failed to send system message: {msg_err}")


class LoanRequestService(ILoanRequestService):
    def __init__(
        self,
        request_repo: ILoanRequestRepository,
        loan_repo: ILoanRepository,
        user_book_repo: IUserBookRepository,
        message_service: Optional[IMessageService] = None,
        db: Optional[AsyncSession] = None
    ):
        self._request_repo = request_repo
        self._loan_repo = loan_repo
        self._user_book_repo = user_book_repo
        self._message_service = message_service
        self._db = db

    async def create_request(self, user_book_id: UUID, requester_id: UUID, message: Optional[str] = None) -> LoanRequest:
        user_book = await self._user_book_repo.get_by_id_for_update(user_book_id)
            
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

        try:
            request = await self._request_repo.create(
                user_book_id=user_book_id,
                requester_id=requester_id,
                owner_id=owner_id,
                message=message,
            )
        except IntegrityError:
            raise ValueError("You already have a pending request for this book copy")
        
        await _publish_system_message_event(
            "loan_request.created",
            request.id,
            "Prośba o wypożyczenie została utworzona.",
            self._message_service
        )

        logger.info(f"Created request: {request.id}")
        return request

    async def accept_request(self, request_id: UUID, owner_id: UUID) -> LoanRequest:
        updated_request = await self._request_repo.update_status_atomic(
            request_id=request_id,
            status="accepted",
            expected_status="pending",
            owner_id=owner_id
        )
        
        if not updated_request:
            request = await self._request_repo.get_by_id(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            if request.owner_id != owner_id:
                raise NotAuthorizedException("You are not the owner of this request")
            if request.status != "pending":
                raise ValueError(f"Cannot accept - current status: {request.status}")
            raise ValueError("Cannot process request")
        
        logger.info(f"Accepted request: {request_id}")
        return updated_request

    async def reject_request(self, request_id: UUID, owner_id: UUID, reason: Optional[str] = None) -> LoanRequest:
        updated_request = await self._request_repo.update_status_atomic(
            request_id=request_id,
            status="rejected",
            expected_status="pending",
            owner_id=owner_id,
            rejection_reason=reason
        )
        
        if not updated_request:
            request = await self._request_repo.get_by_id(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            if request.owner_id != owner_id:
                raise NotAuthorizedException("You are not the owner of this request")
            if request.status != "pending":
                raise ValueError(f"Cannot reject - current status: {request.status}")
            raise ValueError("Cannot process request")
        
        content = "Właściciel odrzucił prośbę o wypożyczenie."
        if reason:
            content += f" Powód: {reason}"
        
        await _publish_system_message_event(
            "loan_request.rejected",
            request_id,
            content,
            self._message_service
        )

        logger.info(f"Rejected request: {request_id}")
        return updated_request

    async def cancel_request(self, request_id: UUID, requester_id: UUID) -> bool:
        updated_request = await self._request_repo.update_status_atomic(
            request_id=request_id,
            status="cancelled",
            expected_status="pending",
            requester_id=requester_id
        )
        
        if not updated_request:
            request = await self._request_repo.get_by_id(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            if request.requester_id != requester_id:
                raise NotAuthorizedException("You are not the author of this request")
            if request.status != "pending":
                raise ValueError(f"Cannot cancel - current status: {request.status}")
            raise ValueError("Cannot process request")
        
        await _publish_system_message_event(
            "loan_request.cancelled",
            request_id,
            "Prośba o wypożyczenie została anulowana przez proszącego.",
            self._message_service
        )

        logger.info(f"Cancelled request: {request_id}")
        return True

    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = "pending", skip: int = 0, limit: int = 100) -> tuple[List[LoanRequest], int]:
        return await self._request_repo.get_incoming_requests(owner_id, status, skip, limit)

    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List[LoanRequest], int]:
        return await self._request_repo.get_outgoing_requests(requester_id, status, skip, limit)

    async def get_by_id(self, request_id: UUID) -> Optional[LoanRequest]:
        return await self._request_repo.get_by_id(request_id)

    async def update(self, request_id: UUID, data: dict) -> LoanRequest:
        updated = await self._request_repo.partial_update(request_id, data)
        
        if not updated:
            request = await self._request_repo.get_by_id(request_id)
            if not request:
                raise LoanRequestNotFoundException(request_id)
            raise ValueError("Failed to update request")
        
        logger.info(f"Updated request: {request_id}")
        return updated

    async def get_summary(self, user_id: UUID) -> dict:
        incoming_pending = await self._request_repo.count_pending_for_owner(user_id)
        outgoing_pending = await self._request_repo.count_pending_for_requester(user_id)

        return {
            "incoming_pending": incoming_pending,
            "outgoing_pending": outgoing_pending,
        }
