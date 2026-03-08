"""Book-related interfaces."""
from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from src.schemas.book import BookCreate, BookUpdate, BookResponse


class IBookService(ABC):
    """Main interface for book catalog operations."""

    @abstractmethod
    async def create_book(self, book: "BookCreate") -> "BookResponse": ...

    @abstractmethod
    async def get_book(self, book_id: UUID) -> "BookResponse": ...

    @abstractmethod
    async def list_books(self, skip: int = 0, limit: int = 100) -> list["BookResponse"]: ...

    @abstractmethod
    async def get_user_books(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list["BookResponse"]: ...

    @abstractmethod
    async def get_community_books(
        self,
        user_id: UUID | None,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        search: str | None = None,
        author: str | None = None
    ) -> list["BookResponse"]: ...

    @abstractmethod
    async def count_community_books(
        self,
        user_id: UUID | None,
        status: str | None = None,
        search: str | None = None,
        author: str | None = None
    ) -> int: ...

    @abstractmethod
    async def search_books(self, query: str, filters: dict) -> list["BookResponse"]: ...

    @abstractmethod
    async def add_book(self, user_id: UUID, data: "BookCreate") -> "BookResponse": ...

    @abstractmethod
    async def update_book(self, book_id: UUID, user_id: UUID, data: "BookUpdate") -> "BookResponse": ...

    @abstractmethod
    async def delete_book(self, book_id: UUID, user_id: UUID) -> None: ...

    @abstractmethod
    async def toggle_lendable(self, book_id: UUID, user_id: UUID, is_lendable: bool) -> "BookResponse": ...

    @abstractmethod
    async def enrich_book_with_ai(self, book_data: dict) -> tuple[dict, str | None]: ...

    @abstractmethod
    async def get_by_isbn(self, isbn: str) -> "BookResponse | None": ...

    @abstractmethod
    async def search(
        self,
        query: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list["BookResponse"], int]: ...


class IUserBookService(ABC):
    """Interface for UserBook service managing user's book collection."""

    @abstractmethod
    async def add_book_to_user(self, user_id: UUID, book_id: UUID, **kwargs) -> "BookResponse": ...

    @abstractmethod
    async def get_user_library(self, user_id: UUID) -> list: ...

    @abstractmethod
    async def remove_book_from_user(self, user_id: UUID, book_id: UUID) -> bool: ...

    @abstractmethod
    async def update_book_status(self, user_id: UUID, book_id: UUID, status: str) -> "BookResponse": ...

    @abstractmethod
    async def toggle_lendable(self, user_book_id: UUID) -> "BookResponse": ...


class IBookMetadataProvider(ABC):
    """Interface for external book metadata providers (Google Books, etc)."""

    @abstractmethod
    async def fetch_by_isbn(self, isbn: str) -> Optional["BookMetadata"]:
        pass

    @abstractmethod
    async def search_by_title(self, title: str, max_results: int = 10) -> List["BookMetadata"]:
        pass


class IMetadataProviderFactory(ABC):
    @abstractmethod
    def create_provider(self) -> IBookMetadataProvider:
        pass


class BookMetadata:
    def __init__(
        self,
        isbn: str,
        title: str,
        author: str,
        description: Optional[str] = None,
        publisher: Optional[str] = None,
        publication_year: Optional[int] = None,
        page_count: Optional[int] = None,
        language: Optional[str] = None,
        genre: Optional[str] = None,
        cover_url: Optional[str] = None
    ):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.description = description
        self.publisher = publisher
        self.publication_year = publication_year
        self.page_count = page_count
        self.language = language
        self.genre = genre
        self.cover_url = cover_url
