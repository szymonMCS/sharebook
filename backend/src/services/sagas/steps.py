import logging
from uuid import UUID
from typing import Optional
from src.services.interfaces import ISagaStep, SagaContext
from src.services.interfaces import ILoanRequestService, ILoanService, ILibraryManagementService
from src.core.constants import MAX_ACTIVE_LOANS

logger = logging.getLogger(__name__)


class ValidateRequestStep(ISagaStep):
    name = "validate_request"

    def __init__(self, request_service: ILoanRequestService, loan_service: ILoanService):
        self._request_service = request_service
        self._loan_service = loan_service

    async def execute(self, context: SagaContext) -> bool:
        try:
            request_id = UUID(context.payload["request_id"])
            owner_id = UUID(context.payload["owner_id"])

            request = await self._request_service.get_by_id(request_id)
            if not request:
                logger.error(f"Request {request_id} not found")
                return False

            if request.owner_id != owner_id:
                logger.error(f"User {owner_id} is not owner of request {request_id}")
                return False

            if request.status != "pending":
                logger.error(f"Request {request_id} status is {request.status}, not pending")
                return False

            can_borrow = await self._loan_service.can_borrow_more(request.requester_id)
            if not can_borrow:
                logger.error(f"Requester {request.requester_id} has reached max loans ({MAX_ACTIVE_LOANS})")
                return False

            context.payload["user_book_id"] = str(request.user_book_id)
            context.payload["requester_id"] = str(request.requester_id)
            logger.info(f"Request {request_id} validated successfully")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    async def compensate(self, context: SagaContext) -> bool:
        return True


class CreateLoanStep(ISagaStep):
    name = "create_loan"

    def __init__(self, loan_service: ILoanService, request_service: ILoanRequestService):
        self._loan_service = loan_service
        self._request_service = request_service

    async def execute(self, context: SagaContext) -> bool:
        try:
            request_id = UUID(context.payload["request_id"])
            owner_id = UUID(context.payload["owner_id"])

            request = await self._request_service.get_by_id(request_id)
            loan = await self._loan_service.create_loan(user_book_id=request.user_book_id, borrower_id=request.requester_id, lender_id=owner_id)

            context.payload["loan_id"] = str(loan.id)
            context.payload["user_book_id"] = str(request.user_book_id)
            logger.info(f"Created loan {loan.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create loan: {e}")
            return False

    async def compensate(self, context: SagaContext) -> bool:
        try:
            loan_id = context.payload.get("loan_id")
            if loan_id:
                await self._loan_service.delete_loan(UUID(loan_id))
                logger.info(f"Compensated loan {loan_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to compensate loan: {e}")
            return False


class UpdateBookStatusStep(ISagaStep):
    name = "update_book_status"

    def __init__(self, library_service: ILibraryManagementService):
        self._library_service = library_service

    async def execute(self, context: SagaContext) -> bool:
        try:
            owner_id = UUID(context.payload["owner_id"])
            user_book_id = UUID(context.payload["user_book_id"])

            await self._library_service.update_status(user_id=owner_id, user_book_id=user_book_id, status="borrowed")
            logger.info("Updated book status to borrowed")
            return True
        except Exception as e:
            logger.error(f"Failed to update book status: {e}")
            return False

    async def compensate(self, context: SagaContext) -> bool:
        try:
            owner_id = UUID(context.payload["owner_id"])
            user_book_id = UUID(context.payload["user_book_id"])

            await self._library_service.update_status(user_id=owner_id, user_book_id=user_book_id, status="available")
            logger.info("Compensated book status to available")
            return True
        except Exception as e:
            logger.error(f"Failed to compensate book status: {e}")
            return False


class AcceptRequestStep(ISagaStep):
    name = "accept_request"

    def __init__(self, request_service: ILoanRequestService):
        self._request_service = request_service

    async def execute(self, context: SagaContext) -> bool:
        try:
            request_id = UUID(context.payload["request_id"])
            owner_id = UUID(context.payload["owner_id"])

            await self._request_service.accept_request(request_id=request_id, owner_id=owner_id)
            logger.info(f"Accepted request {request_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to accept request: {e}")
            return False

    async def compensate(self, context: SagaContext) -> bool:
        try:
            request_id = UUID(context.payload["request_id"])
            owner_id = UUID(context.payload["owner_id"])

            await self._request_service.reject_request(request_id=request_id, owner_id=owner_id, reason="Saga compensation")
            logger.info(f"Compensated request {request_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to compensate request: {e}")
            return False
