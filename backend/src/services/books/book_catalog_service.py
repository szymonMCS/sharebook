import logging
from uuid import UUID
from typing import Optional, List
from src.services.interfaces.books import IBookCatalogService
from database.interfaces import IBookRepository
from src.schemas.book import BookCreate, BookUpdate, BookResponse
from src.core.exceptions import BookNotFoundException, DuplicateISBNException

logger = logging.getLogger(__name__)


class BookCatalogService(IBookCatalogService):

    def __init__(self, book_repo: IBookRepository):
        self._repo = book_repo

    async def get_by_id(self, book_id: UUID) -> BookResponse:
        book = await self._repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(book_id)
        return BookResponse.model_validate(book)

    async def get_by_isbn(self, isbn: str) -> Optional[BookResponse]:
        book = await self._repo.get_by_isbn(isbn)
        if book:
            return BookResponse.model_validate(book)
        return None

    async def search(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[BookResponse], int]:
        books, total = await self._repo.search(
            query=query,
            author=author,
            genre=genre,
            skip=skip,
            limit=limit
        )
        return [BookResponse.model_validate(b) for b in books], total

    async def create(self, data: BookCreate) -> BookResponse:
        if data.isbn:
            existing = await self._repo.get_by_isbn(data.isbn)
            if existing:
                raise DuplicateISBNException(data.isbn)

        book = await self._repo.create(
            isbn=data.isbn,
            title=data.title,
            author=data.author,
            description=data.description,
            publisher=data.publisher,
            publication_year=data.publication_year,
            page_count=data.page_count,
            language=data.language,
            genre=data.genre,
            cover_url=data.cover_url
        )
        logger.info(f"Book created in catalog: {book.id} (ISBN: {book.isbn})")
        return BookResponse.model_validate(book)

    async def update(self, book_id: UUID, data: BookUpdate) -> BookResponse:
        book = await self._repo.update(book_id, data)
        if not book:
            raise BookNotFoundException(book_id)
        logger.info(f"Book updated in catalog: {book_id}")
        return BookResponse.model_validate(book)
