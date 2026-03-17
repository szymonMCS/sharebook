from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.loan import LoanResponse, LoanRequestResponse, BorrowedBookResponse, LentBookResponse

BorrowedBookResponse = "BorrowedBookResponse"
LentBookResponse = "LentBookResponse"


class ILoanService(ABC):
    @abstractmethod
    async def create_loan(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID) -> "LoanResponse":
        """Create a loan record (low-level)."""
        pass
    
    @abstractmethod
    async def borrow_book(self, user_id: UUID, user_book_id: UUID) -> "LoanResponse":
        """Borrow a book with limit checks and validation (high-level).
        
        Args:
            user_id: The user borrowing the book
            user_book_id: The user_book copy to borrow
            
        Returns:
            LoanResponse: The created loan
            
        Raises:
            ValueError: If user has reached max active loans or book not available
        """
        pass
    
    @abstractmethod
    async def return_book(self, loan_id: UUID, user_id: UUID) -> "LoanResponse":
        """Return a borrowed book."""
        pass
    
    @abstractmethod
    async def get_user_loans(self, user_id: UUID) -> List["LoanResponse"]:
        """Get all active loans for a user (both borrowed and lent)."""
        pass
    
    @abstractmethod
    async def get_loan(self, loan_id: UUID) -> "LoanResponse":
        """Get a loan by ID.
        
        Raises:
            LoanNotFoundException: If loan not found
        """
        pass
    
    @abstractmethod
    async def get_borrowed_books(self, borrower_id: UUID, status: Optional[str] = None) -> List["BorrowedBookResponse"]:
        """Get borrowed books with details."""
        pass
    
    @abstractmethod
    async def get_lent_books(self, lender_id: UUID, status: Optional[str] = None) -> List["LentBookResponse"]:
        """Get lent books with details."""
        pass
    
    @abstractmethod
    async def can_borrow_more(self, borrower_id: UUID) -> bool:
        """Check if user can borrow more books."""
        pass
    
    @abstractmethod
    async def get_loan_by_id(self, loan_id: UUID) -> Optional["LoanResponse"]:
        """Get a loan by ID (returns None if not found)."""
        pass
    
    @abstractmethod
    async def create_loan(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID) -> "LoanResponse":
        """Create a loan record (low-level)."""
        pass
    
    @abstractmethod
    async def count_active_loans(self, borrower_id: UUID) -> int:
        """Count active loans for a borrower."""
        pass
    
    @abstractmethod
    async def delete_loan(self, loan_id: UUID) -> bool:
        """Delete a loan record."""
        pass


class ILoanRequestService(ABC):
    @abstractmethod
    async def create_request(self, user_book_id: UUID, requester_id: UUID, message: Optional[str] = None) -> "LoanRequestResponse":
        """Create a new loan request."""
        pass
    
    @abstractmethod
    async def reserve_request(self, request_id: UUID, owner_id: UUID) -> "LoanRequestResponse":
        """Reserve a book for a borrower.
        
        Args:
            request_id: The request to reserve
            owner_id: The book owner making the reservation
            
        Returns:
            LoanRequestResponse for the reserved request
        """
        pass
    
    @abstractmethod
    async def accept_request(self, request_id: UUID, owner_id: UUID) -> "LoanRequestResponse":
        """Accept a loan request and create loan record."""
        pass
    
    @abstractmethod
    async def reject_request(self, request_id: UUID, owner_id: UUID, reason: Optional[str] = None) -> "LoanRequestResponse":
        """Reject a loan request."""
        pass
    
    @abstractmethod
    async def cancel_request(self, request_id: UUID, requester_id: UUID) -> bool:
        """Cancel a pending loan request."""
        pass
    
    @abstractmethod
    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = "pending", skip: int = 0, limit: int = 100) -> tuple[List["LoanRequestResponse"], int]:
        """Get incoming loan requests for an owner."""
        pass
    
    @abstractmethod
    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List["LoanRequestResponse"], int]:
        """Get outgoing loan requests for a borrower."""
        pass
    
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional["LoanRequestResponse"]:
        """Get a request by ID."""
        pass
    
    @abstractmethod
    async def update(self, request_id: UUID, data: dict) -> "LoanRequestResponse":
        """Update a request."""
        pass
    
    @abstractmethod
    async def get_summary(self, user_id: UUID) -> dict:
        """Get request summary for a user."""
        pass
