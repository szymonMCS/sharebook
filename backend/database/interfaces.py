from abc import ABC, abstractmethod
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Book, UserBook, Loan, LoanRequest, Message

T = TypeVar("T")


class IRepository(ABC, Generic[T]):    
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        pass
    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass
    @abstractmethod
    async def create(self, obj_in: dict) -> T:
        pass
    @abstractmethod
    async def update(self, db_obj: T, obj_in: dict) -> T:
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        pass


class IUserRepository(ABC):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
    @abstractmethod
    async def get(self, id: UUID) -> Optional["User"]:
        pass
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional["User"]:
        pass
    @abstractmethod
    async def get_by_id_for_update(self, id: UUID) -> Optional["User"]:
        pass
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional["User"]:
        pass
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        pass
    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> tuple[List["User"], int]:
        pass
    @abstractmethod
    async def get_multi_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List["User"], int]:
        pass
    @abstractmethod
    async def create_user(
        self,
        email: str,
        hashed_password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        location: Optional[str] = None,
        phone: Optional[str] = None,
        role: str = "reader",
        is_active: bool = True
    ) -> "User":
        pass
    @abstractmethod
    async def update(self, db_obj: "User", obj_in: dict) -> "User":
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def count_user_books(self, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_all(self) -> int:
        pass
    @abstractmethod
    async def count_new_since(self, since: datetime) -> int:
        pass
    @abstractmethod
    async def count_active_borrowers(self, since: datetime) -> int:
        pass
    @abstractmethod
    async def get_daily_registrations(self, days: int) -> List[dict]:
        pass


class IBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Book]:
        pass
    @abstractmethod
    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        pass
    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[Book]:
        pass
    @abstractmethod
    async def get_with_owners(self, book_id: UUID) -> Optional[Book]:
        pass
    @abstractmethod
    async def create(self, obj_in: dict) -> Book:
        pass
    @abstractmethod
    async def create_book_from_dict(self, book_data: dict) -> Book:
        pass
    @abstractmethod
    async def update(self, db_obj: Book, obj_in: dict) -> Book:
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def search(self, query: str, filters: dict) -> List[Book]:
        pass
    @abstractmethod
    async def count_all(self) -> int:
        pass
    @abstractmethod
    async def count_new_since(self, since: datetime) -> int:
        pass
    @abstractmethod
    async def get_available_for_community(
        self,
        exclude_user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None
    ) -> List[tuple[Book, UserBook, User]]:
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
    @abstractmethod
    async def search_by_title(self, query: str) -> List[Book]:
        pass
    @abstractmethod
    async def enrich_book(self, book_id: UUID, enrichment_data: dict) -> Optional[Book]:
        pass


class IUserBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def get_by_id_for_update(self, id: UUID) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def get_by_user_and_book(self, user_id: UUID, book_id: UUID) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def get_user_library(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[UserBook]:
        pass
    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[UserBook]:
        pass
    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        book_id: UUID,
        status: str = "available",
        condition: Optional[str] = None,
        is_lendable: bool = True
    ) -> UserBook:
        pass
    @abstractmethod
    async def update(
        self,
        id: UUID,
        status: Optional[str] = None,
        condition: Optional[str] = None,
        is_lendable: Optional[bool] = None,
        commit: bool = True
    ) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[UserBook]:
        pass
    @abstractmethod
    async def count_by_user(self, user_id: UUID, status: Optional[str] = None) -> int:
        pass
    @abstractmethod
    async def count_all(self) -> int:
        pass


class ILoanRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Loan]:
        pass
    @abstractmethod
    async def get_by_id_for_update(self, id: UUID) -> Optional[Loan]:
        pass
    @abstractmethod
    async def get_by_borrower(self, borrower_id: UUID, skip: int = 0, limit: int = 100) -> List[Loan]:
        pass
    @abstractmethod
    async def get_by_lender(self, lender_id: UUID, skip: int = 0, limit: int = 100) -> List[Loan]:
        pass
    @abstractmethod
    async def get_active_loans(self, user_id: UUID) -> List[Loan]:
        pass
    @abstractmethod
    async def get_overdue_loans(self) -> List[Loan]:
        pass
    @abstractmethod
    async def create(
        self,
        user_book_id: UUID,
        borrower_id: UUID,
        lender_id: UUID,
        loan_duration_days: int = 14,
        commit: bool = True
    ) -> Loan:
        pass
    @abstractmethod
    async def update(self, db_obj: Loan, obj_in: dict) -> Loan:
        pass
    @abstractmethod
    async def mark_returned(self, loan_id: UUID) -> Optional[Loan]:
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def count_active_for_borrower(self, borrower_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_all(self) -> int:
        pass
    @abstractmethod
    async def count_active(self) -> int:
        pass


class ILoanRequestRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def get_by_id_for_update(self, id: UUID) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def get_incoming_requests(self, owner_id: UUID) -> List[LoanRequest]:
        pass
    @abstractmethod
    async def get_outgoing_requests(self, requester_id: UUID) -> List[LoanRequest]:
        pass
    @abstractmethod
    async def get_active_for_user_book(self, user_book_id: UUID) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def create(
        self,
        user_book_id: UUID,
        requester_id: UUID,
        owner_id: UUID,
        message: Optional[str] = None
    ) -> LoanRequest:
        pass
    @abstractmethod
    async def update_status(
        self,
        request_id: UUID,
        status: str,
        rejection_reason: Optional[str] = None,
        commit: bool = True
    ) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def cancel(self, request_id: UUID) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def get_conversation(self, request_id: UUID) -> List[Message]:
        pass


class IMessageRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Message]:
        pass
    @abstractmethod
    async def get_by_loan_request(self, loan_request_id: UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        pass
    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def create(
        self,
        loan_request_id: UUID,
        sender_id: UUID,
        content: str,
        message_type: str = "text"
    ) -> Message:
        pass
    @abstractmethod
    async def mark_as_read(self, message_id: UUID) -> Optional[Message]:
        pass
    @abstractmethod
    async def mark_all_as_read(self, loan_request_id: UUID, user_id: UUID) -> int:
        pass
