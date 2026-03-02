from abc import ABC, abstractmethod
from uuid import UUID
from typing import TypeVar, Generic, Optional, List, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from database.models import User, Book, UserBook


T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        """pobieranie encji po id"""
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
