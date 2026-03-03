from abc import ABC, abstractmethod
from uuid import UUID
from typing import TypeVar, Generic, Optional, List, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from database.models import User, Book, UserBook, Loan, LoanRequest, Message


T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        """pobieranie encji po id"""
        pass
    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]: 
        """pobierz liste encji z paginacja"""
        pass
    @abstractmethod
    async def create(self, obj_in: dict) -> T:
        """tworzenie encji"""
        pass
    @abstractmethod
    async def update(self, db_obj: T, obj_in: dict) -> T:
        """aktualizujemy encje"""
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """usuwamy encje po id"""
        pass
    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """sprawdz wystepowanie encji"""
        pass


class IUserRepository(IRepository["User"], ABC):
    """interfejs użytkowników"""
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional["User"]:
        pass
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional["User"]:
        pass
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        pass


class IBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional["Book"]:
        pass
    @abstractmethod
    async def get_by_isbn(self, isbn: str) -> Optional["Book"]:
        pass
    @abstractmethod
    async def create(self, isbn: str, title: str, **kwargs) -> "Book":
        pass
    @abstractmethod
    async def update(self, id: UUID, book_data: dict) -> Optional["Book"]:
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List["Book"]:
        pass
    @abstractmethod
    async def search(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List["Book"], int]:
        """Wyszukaj książki. Zwraca (lista, całkowita_liczba)."""
        pass


class IUserBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional["UserBook"]:
        pass
    @abstractmethod
    async def get_by_user_and_book(self, user_id: UUID, book_id: UUID) -> Optional["UserBook"]:
        pass
    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        book_id: UUID,
        status: str = "available",
        condition: Optional[str] = None,
        is_lendable: bool = True
    ) -> "UserBook":
        pass
    @abstractmethod
    async def update(
        self,
        id: UUID,
        status: Optional[str] = None,
        condition: Optional[str] = None,
        is_lendable: Optional[bool] = None
    ) -> Optional["UserBook"]:
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_user_library(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[tuple["UserBook", "Book"]]:
        pass
    @abstractmethod
    async def get_available_for_community(
        self,
        exclude_user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[tuple["Book", "UserBook", "User"]]:
        pass
    @abstractmethod
    async def count_available_for_community(
        self,
        exclude_user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None
    ) -> int:
        pass


class ILoanRepository(ABC):
    @abstractmethod
    async def get_by_id(self, loan_id: UUID) -> Optional["Loan"]:
        pass
    @abstractmethod
    async def create(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID, loan_duration_days: int = 14) -> "Loan":
        pass
    @abstractmethod
    async def mark_returned(self, loan_id: UUID) -> Optional["Loan"]:
        pass
    @abstractmethod
    async def get_borrower_loans(self, borrower_id: UUID, status: Optional[str] = None) -> List["Loan"]:
        pass
    @abstractmethod
    async def get_lender_loans(self, lender_id: UUID, status: Optional[str] = None) -> List["Loan"]:
        pass
    @abstractmethod
    async def count_active_for_borrower(self, borrower_id: UUID) -> int:
        pass


class ILoanRequestRepository(ABC):
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional["LoanRequest"]:
        pass
    @abstractmethod
    async def create(self, user_book_id: UUID, requester_id: UUID, owner_id: UUID, message: Optional[str] = None) -> "LoanRequest":
        pass
    @abstractmethod
    async def update_status(self, request_id: UUID, status: str, rejection_reason: Optional[str] = None) -> Optional["LoanRequest"]:
        pass
    @abstractmethod
    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = None) -> List["LoanRequest"]:
        pass
    @abstractmethod
    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None) -> List["LoanRequest"]:
        pass
    @abstractmethod
    async def has_pending_request(self, user_book_id: UUID, requester_id: UUID) -> bool:
        pass
    @abstractmethod
    async def count_pending_for_owner(self, owner_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_pending_for_requester(self, requester_id: UUID) -> int:
        pass


class IMessageRepository(ABC):
    @abstractmethod
    async def create(
        self,
        loan_request_id: UUID,
        sender_id: UUID,
        content: str,
        message_type: str = "text"
    ) -> "Message":
        pass
    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Optional["Message"]:
        pass
    @abstractmethod
    async def get_by_loan_request(self, loan_request_id: UUID, include_sender: bool = True) -> List["Message"]:
        pass
    @abstractmethod
    async def get_unread_count(self, loan_request_id: UUID, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def mark_as_read(self, message_id: UUID) -> bool:
        pass
    @abstractmethod
    async def mark_all_as_read(self, loan_request_id: UUID, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def create_system_message(self, loan_request_id: UUID, content: str) -> "Message":
        pass


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def session(self) -> AsyncSession:
        pass
    @property
    @abstractmethod
    def users(self) -> "IUserRepository":
        pass
    @property
    @abstractmethod
    def books(self) -> "IBookRepository":
        pass
    @property
    @abstractmethod
    def user_books(self) -> "IUserBookRepository":
        pass
    @property
    @abstractmethod
    def loans(self) -> "ILoanRepository":
        pass
    @property
    @abstractmethod
    def loan_requests(self) -> "ILoanRequestRepository":
        pass
    @property
    @abstractmethod
    def messages(self) -> "IMessageRepository":
        pass
    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        pass
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        pass
    @abstractmethod
    async def commit(self) -> None:
        pass
    @abstractmethod
    async def rollback(self) -> None:
        pass
    @abstractmethod
    async def flush(self) -> None:
        pass
