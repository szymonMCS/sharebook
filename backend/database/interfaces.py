from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic
from datetime import datetime
from uuid import UUID
from database.models import User, Book, UserBook, Loan, LoanRequest, Message


T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]: ...
    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]: ...
    @abstractmethod
    async def create(self, obj_in: dict) -> T: ...
    @abstractmethod
    async def update(self, db_obj: T, obj_in: dict) -> T: ...
    @abstractmethod
    async def delete(self, id: UUID) -> bool: ...
    @abstractmethod
    async def exists(self, id: UUID) -> bool: ...


class IUserRepository(ABC):
    @abstractmethod
    async def get(self, id: UUID) -> Optional[User]:
        pass
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[User]:
        pass
    @abstractmethod
    async def get_by_id_for_update(self, id: UUID) -> Optional[User]:
        pass
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
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
    ) -> User:
        pass
    @abstractmethod
    async def update(self, db_obj: User, obj_in: dict) -> User:
        pass
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_multi_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
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
    async def get(self, book_id: UUID) -> Optional[Book]:
        pass
    @abstractmethod
    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
        pass
    @abstractmethod
    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        pass
    @abstractmethod
    async def create(self, book_data: dict) -> Book:
        pass
    @abstractmethod
    async def update(self, book_id: UUID, update_data: dict) -> Optional[Book]:
        pass
    @abstractmethod
    async def delete(self, book_id: UUID) -> bool:
        pass
    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 20, filters: Optional[dict] = None) -> tuple[List[Book], int]:
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
    ) -> List:
        pass
    @abstractmethod
    async def count_available_for_community(self, exclude_user_id: Optional[UUID] = None, status: Optional[str] = None, search: Optional[str] = None, author: Optional[str] = None) -> int:
        pass
    @abstractmethod
    async def count_all(self) -> int:
        pass
    @abstractmethod
    async def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Book]:
        pass
    @abstractmethod
    async def get_multi_with_search(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[List[Book], int]:
        pass
    @abstractmethod
    async def get_book_stats(self, book_id: UUID) -> dict:
        pass
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Book]:
        pass
    @abstractmethod
    async def create_book_from_dict(self, book_data: dict) -> Book:
        pass
    @abstractmethod
    async def get_daily_additions(self, days: int = 30) -> List[dict]:
        pass
    @abstractmethod
    async def get_popular_books(self, days: int = 30, limit: int = 10) -> List[dict]:
        pass


class IUserBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_book_id: UUID) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def get_by_id_for_update(self, user_book_id: UUID) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def get_user_library(self, user_id: UUID, status: Optional[str] = None) -> List[tuple]:
        pass
    @abstractmethod
    async def create(self, obj_in: dict) -> UserBook:
        pass
    @abstractmethod
    async def update(self, user_book_id: UUID, obj_in: dict) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def update_status(self, user_book_id: UUID, status: str) -> Optional[UserBook]:
        pass
    @abstractmethod
    async def delete(self, user_book_id: UUID) -> bool:
        pass
    @abstractmethod
    async def count_user_library(self, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_lent_by_user(self, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        pass
    @abstractmethod
    async def get_owners_for_book(self, book_id: UUID) -> List[User]:
        pass
    @abstractmethod
    async def get_by_user_and_book(self, user_id: UUID, book_id: UUID) -> Optional[UserBook]:
        pass


class ILoanRepository(ABC):
    @abstractmethod
    async def get_by_id(self, loan_id: UUID) -> Optional[Loan]:
        pass
    @abstractmethod
    async def get_borrower_loans(self, borrower_id: UUID, status: Optional[str] = None) -> List[Loan]:
        pass
    @abstractmethod
    async def get_lender_loans(self, lender_id: UUID, status: Optional[str] = None) -> List[Loan]:
        pass
    @abstractmethod
    async def create(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID, loan_duration_days: int = 14) -> Loan:
        pass
    @abstractmethod
    async def mark_returned(self, loan_id: UUID) -> Optional[Loan]:
        pass
    @abstractmethod
    async def delete(self, loan_id: UUID) -> bool:
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
    @abstractmethod
    async def get_daily_stats(self, days: int = 30) -> List[dict]:
        pass
    @abstractmethod
    async def get_average_duration(self, days: int = 30) -> float:
        pass


class ILoanRequestRepository(ABC):
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def get_by_id_for_update(self, request_id: UUID) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List[LoanRequest], int]:
        pass
    @abstractmethod
    async def get_outgoing_requests(self, requester_id: UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[List[LoanRequest], int]:
        pass
    @abstractmethod
    async def create(self, user_book_id: UUID, requester_id: UUID, owner_id: UUID, message: Optional[str] = None) -> LoanRequest:
        pass
    @abstractmethod
    async def update_status(self, request_id: UUID, status: str, rejection_reason: Optional[str] = None) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def delete(self, request_id: UUID) -> bool:
        pass
    @abstractmethod
    async def has_pending_request(self, user_book_id: UUID, requester_id: UUID) -> bool:
        pass
    @abstractmethod
    async def partial_update(self, request_id: UUID, data: dict) -> Optional[LoanRequest]:
        pass
    @abstractmethod
    async def get_pending_for_book(self, user_book_id: UUID) -> List[LoanRequest]:
        pass
    @abstractmethod
    async def count_pending_for_book(self, user_book_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_reserved_for_book(self, user_book_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_pending_for_owner(self, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def count_pending_for_requester(self, user_id: UUID) -> int:
        pass


class IMessageRepository(ABC):
    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        pass
    @abstractmethod
    async def get_by_loan_request(self, loan_request_id: UUID, skip: int = 0, limit: int = 100, include_sender: bool = False) -> List[Message]:
        pass
    @abstractmethod
    async def create(self, loan_request_id: UUID, sender_id: UUID, content: str, message_type: str = "text") -> Message:
        pass
    @abstractmethod
    async def mark_as_read(self, message_id: UUID) -> Optional[Message]:
        pass
    @abstractmethod
    async def mark_all_as_read(self, loan_request_id: UUID, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def get_unread_count(self, loan_request_id: UUID, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def create_system_message(self, loan_request_id: UUID, content: str) -> Message:
        pass
