from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.loan import LoanResponse, LoanRequestResponse


class ILoanService(ABC):
    @abstractmethod
    async def create_loan(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID) -> "LoanResponse":
        pass
    @abstractmethod
    async def return_book(self, loan_id: UUID, user_id: UUID) -> "LoanResponse":
        pass
    @abstractmethod
    async def get_borrowed_books(self, borrower_id: UUID, status: Optional[str] = None) -> List["LoanResponse"]:
        pass
    @abstractmethod
    async def get_lent_books(self, lender_id: UUID, status: Optional[str] = None) -> List["LoanResponse"]:
        pass
    @abstractmethod
    async def can_borrow_more(self, borrower_id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_loan_by_id(self, loan_id: UUID) -> Optional["LoanResponse"]:
        pass
    @abstractmethod
    async def count_active_loans(self, borrower_id: UUID) -> int:
        pass
    @abstractmethod
    async def delete_loan(self, loan_id: UUID) -> bool:
        pass


class ILoanRequestService(ABC):
    @abstractmethod
    async def create_request(self, user_book_id: UUID, requester_id: UUID, message: Optional[str] = None) -> "LoanRequestResponse":
        pass
    @abstractmethod
    async def accept_request(self, request_id: UUID, owner_id: UUID) -> "LoanRequestResponse":
        pass
    @abstractmethod
    async def reject_request(self, request_id: UUID, owner_id: UUID, reason: Optional[str] = None) -> "LoanRequestResponse":
        pass
    @abstractmethod
    async def cancel_request(self, request_id: UUID, requester_id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = "pending", skip: int = 0, limit: int = 100) -> tuple[List["LoanRequestResponse"], int]:
        pass
    @abstractmethod
    async def get_outgoing_requests(self,requester_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List["LoanRequestResponse"], int]:
        pass
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional["LoanRequestResponse"]:
        pass
    @abstractmethod
    async def update(self, request_id: UUID, data: dict) -> "LoanRequestResponse":
        pass
    @abstractmethod
    async def get_summary(self, user_id: UUID) -> dict:
        pass
