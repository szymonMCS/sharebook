from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID
from typing import TypeVar, Generic, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from database.models import User, Book, Loan, LoanRequest

T = TypeVar("T")         
CreateT = TypeVar("CreateT") 
UpdateT = TypeVar("UpdateT")  


class IRepository(ABC, Generic[T, CreateT, UpdateT]):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        ...
    
    @abstractmethod
    async def create(self, obj: CreateT) -> T:
        ...
    
    @abstractmethod
    async def update(self, id: UUID, obj: UpdateT) -> T | None:
        ...
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        ...
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        ...


class IBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> "Book | None":
        ...
    
    @abstractmethod
    async def get_by_isbn(self, isbn: str) -> "Book | None":
        ...
    
    @abstractmethod
    async def create(self, isbn: str, title: str, **kwargs) -> "Book":
        ...
    
    @abstractmethod
    async def update(self, id: UUID, book_data) -> "Book | None":
        ...
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        ...
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list["Book"]:
        ...
    
    @abstractmethod
    async def search(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list["Book"], int]:
        ...
    
    @abstractmethod
    async def update_cover_path(self, book_id: UUID, cover_path: str) -> None:
        ...


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> "User | None": ...
    
    @abstractmethod
    async def get_by_email(self, email: str) -> "User | None":
        ...
    
    @abstractmethod
    async def create(self, email: str, hashed_password: str, **kwargs) -> "User": ...
    
    @abstractmethod
    async def update(self, user: "User", **kwargs) -> "User": ...


class IUserBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> "UserBook | None":
        ...
    
    @abstractmethod
    async def get_by_user_and_book(self, user_id: UUID, book_id: UUID) -> "UserBook | None":
        ...
    
    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        book_id: UUID,
        status: str = "available",
        condition: Optional[str] = None,
        is_lendable: bool = True
    ) -> "UserBook":
        ...
    
    @abstractmethod
    async def update(
        self,
        id: UUID,
        status: Optional[str] = None,
        condition: Optional[str] = None,
        is_lendable: Optional[bool] = None
    ) -> "UserBook | None":
        ...
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        ...
    
    @abstractmethod
    async def get_user_library(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[tuple["UserBook", "Book"]]:
        ...
    
    @abstractmethod
    async def get_available_for_community(
        self,
        exclude_user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> list[tuple["Book", "UserBook", "User"]]:
        ...
    
    @abstractmethod
    async def count_available_for_community(
        self,
        exclude_user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None
    ) -> int:
        ...


class ILoanRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> "Loan | None": ...
    
    @abstractmethod
    async def create(
        self, 
        user_id: UUID, 
        book_id: UUID, 
        owner_id: UUID, 
        due_date: datetime, 
        **kwargs
    ) -> "Loan": ...
    
    @abstractmethod
    async def get_user_loans(self, user_id: UUID) -> list["Loan"]: ...
    
    @abstractmethod
    async def get_owner_loans(self, owner_id: UUID) -> list["Loan"]: ...
    
    @abstractmethod
    async def update_status(self, loan_id: UUID, status: str) -> "Loan | None": ...
    
    @abstractmethod
    async def mark_returned(self, loan_id: UUID) -> "Loan | None": ...
    
    @abstractmethod
    async def commit(self) -> None:
        ...