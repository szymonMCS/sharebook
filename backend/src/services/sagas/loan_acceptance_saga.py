import logging
from uuid import UUID
from typing import Optional
from dataclasses import dataclass
from src.services.interfaces import (
    ILoanRequestService,
    ILoanService,
    ILibraryManagementService,
    IMessageService,
)
from src.core.constants import MAX_ACTIVE_LOANS

logger = logging.getLogger(__name__)


@dataclass
class AcceptanceResult:
    success: bool
    loan_request_id: Optional[UUID] = None
    loan_id: Optional[UUID] = None
    error_message: Optional[str] = None


class LoanAcceptanceSaga:
    def __init__(
        self,
        loan_request_service: ILoanRequestService,
        loan_service: ILoanService,
        library_service: ILibraryManagementService,
        message_service: Optional[IMessageService] = None,
    ):
        self._request_service = loan_request_service
        self._loan_service = loan_service
        self._library_service = library_service
        self._message_service = message_service
    
    async def execute(self, request_id: UUID, owner_id: UUID) -> AcceptanceResult:
        request = await self._request_service.get_request_details(request_id)
        if not request:
            return AcceptanceResult(
                success=False,
                error_message=f"Loan request {request_id} not found"
            )
        
        if request.owner_id != owner_id:
            return AcceptanceResult(
                success=False,
                error_message="You are not the owner of this request"
            )
        
        if request.status != "pending":
            return AcceptanceResult(
                success=False,
                error_message=f"Cannot accept - current status: {request.status}"
            )
        
        can_borrow = await self._loan_service.can_borrow_more(request.requester_id)
        if not can_borrow:
            return AcceptanceResult(
                success=False,
                error_message=f"Requester has reached the maximum number of active loans ({MAX_ACTIVE_LOANS})"
            )
        
        try:
            loan = await self._loan_service.create_loan(
                user_book_id=request.user_book_id,
                borrower_id=request.requester_id,
                lender_id=owner_id
            )
        except Exception as e:
            logger.error(f"Failed to create loan in saga: {e}")
            return AcceptanceResult(
                success=False,
                error_message="Failed to create loan"
            )
        
        try:
            await self._library_service.update_status(
                user_id=owner_id,
                user_book_id=request.user_book_id,
                status="borrowed"
            )
        except Exception as e:
            logger.error(f"Failed to update book status in saga: {e}")
            await self._compensate_loan_creation(loan.id)
            return AcceptanceResult(
                success=False,
                error_message="Failed to update book status"
            )
        
        try:
            updated_request = await self._request_service.accept_request(
                request_id=request_id,
                owner_id=owner_id
            )
        except Exception as e:
            logger.error(f"Failed to accept request in saga: {e}")
            await self._compensate_book_status(owner_id, request.user_book_id)
            await self._compensate_loan_creation(loan.id)
            return AcceptanceResult(
                success=False,
                error_message="Failed to accept request"
            )
        
        if self._message_service:
            try:
                await self._message_service.add_system_message(
                    request_id,
                    "Właściciel zaakceptował prośbę o wypożyczenie. Książka została wypożyczona."
                )
            except Exception as e:
                logger.warning(f"Failed to send system message in saga: {e}")
                # Nie kompensujemy - wiadomość nie jest krytyczna
        
        logger.info(f"Saga completed successfully: request={request_id}, loan={loan.id}")
        return AcceptanceResult(
            success=True,
            loan_request_id=request_id,
            loan_id=loan.id
        )
    
    async def _compensate_loan_creation(self, loan_id: UUID) -> None:
        try:
            logger.info(f"Compensating loan creation: {loan_id}")
        except Exception as e:
            logger.error(f"Failed to compensate loan creation: {e}")
    
    async def _compensate_book_status(self, owner_id: UUID, user_book_id: UUID) -> None:
        try:
            await self._library_service.update_status(
                user_id=owner_id,
                user_book_id=user_book_id,
                status="available"
            )
            logger.info(f"Compensated book status: {user_book_id}")
        except Exception as e:
            logger.error(f"Failed to compensate book status: {e}")
