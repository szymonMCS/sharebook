import logging
import os
import uuid
from uuid import UUID
from typing import Callable, Awaitable
from database.interfaces import IBookRepository
from src.schemas.book import BookCreate, BookUpdate, BookResponse, CommunityBookResponse, OwnerInfo
from src.core.exceptions import (
    NotFoundException,
    BookNotFoundException,
    NotBookOwnerException,
    DuplicateISBNException,
    BusinessLogicException
)
from src.services.interfaces.books import IBookService
from src.services.book_discovery import UnifiedBookSearch

logger = logging.getLogger(__name__)

VectorSyncCallback = Callable[[UUID, str, str, str | None], Awaitable[None]]


class BookService(IBookService):
    def __init__(self, repository: IBookRepository, vector_sync_callback: VectorSyncCallback | None = None):
        self._repo = repository
        self._vector_sync = vector_sync_callback

    async def create_book(self, book: BookCreate) -> BookResponse:
        db_book = await self._repo.create(book)
        
        if self._vector_sync:
            await self._vector_sync(
                db_book.id, 
                db_book.title, 
                db_book.author, 
                db_book.description
            )
        return BookResponse.model_validate(db_book)

    async def get_book(self, book_id: UUID) -> BookResponse:
        result = await self._repo.get_by_id_with_owner(book_id)
        if not result:
            raise NotFoundException("Book", str(book_id))
        
        book, user_book, owner = result
        return BookResponse(
            id=book.id,
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            description=book.description,
            cover_url=f"/covers/{book.isbn}.jpg" if book.isbn else None,
            publisher=book.publisher,
            publication_year=book.publication_year,
            page_count=book.page_count,
            language=book.language,
            genre=book.genre,
            owner_id=user_book.user_id,
            owner=OwnerInfo(id=owner.id, first_name=owner.first_name, last_name=owner.last_name, location=owner.location),
            status=user_book.status,
            condition=user_book.condition,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

    async def update_book(self, book_id: UUID, user_id: UUID | None = None, book: BookUpdate | None = None) -> BookResponse:
        if book is None and user_id is not None and isinstance(user_id, BookUpdate):
            book = user_id
            user_id = None
        
        existing = await self._repo.get_by_id(book_id)
        if not existing:
            raise BookNotFoundException(book_id)
        if user_id is not None and existing.owner_id != user_id:
            raise NotBookOwnerException()
        updated = await self._repo.update(book_id, book)
        if self._vector_sync:
            await self._vector_sync(updated.id, updated.title, updated.author, updated.description)
        if user_id:
            logger.info(f"Book updated: {book_id} by user {user_id}")
        return BookResponse.model_validate(updated)

    async def enrich_book_with_ai(self, book_data: dict) -> tuple[dict, str | None]:
        external_cover_url: str | None = None
        existing_cover = book_data.get("cover_url")
        is_external_url = existing_cover and (existing_cover.startswith("http://") or existing_cover.startswith("https://"))
        
        if not existing_cover or is_external_url:
            search_query = book_data.get("isbn") or book_data.get("title", "")
            if search_query:
                logger.info(f"AI search for book: {search_query}")
                try:
                    ai_search = UnifiedBookSearch(openai_api_key=os.getenv("OPENAI_API_KEY"))
                    
                    if book_data.get("isbn"):
                        result = await ai_search.search_by_isbn(book_data["isbn"])
                    else:
                        result = await ai_search.search_by_title(book_data.get("title", ""), book_data.get("author"))
                    
                    if result.success and result.data:
                        ai_data = result.data
                        if not book_data.get("description") and ai_data.get("short_description"):
                            book_data["description"] = ai_data["short_description"]
                        if not book_data.get("isbn") and ai_data.get("isbn_13"):
                            book_data["isbn"] = ai_data["isbn_13"]
                        if not book_data.get("cover_url") and ai_data.get("cover_url"):
                            book_data["cover_url"] = ai_data["cover_url"]
                            external_cover_url = ai_data["cover_url"]
                        if not book_data.get("page_count") and ai_data.get("page_count"):
                            book_data["page_count"] = ai_data["page_count"]
                        if not book_data.get("publication_year") and ai_data.get("publication_year"):
                            book_data["publication_year"] = ai_data["publication_year"]
                        if not book_data.get("genre") and ai_data.get("genre"):
                            book_data["genre"] = ai_data["genre"]
                        if not book_data.get("language") and ai_data.get("language"):
                            book_data["language"] = ai_data["language"]
                        if not book_data.get("publisher") and ai_data.get("publisher"):
                            book_data["publisher"] = ai_data["publisher"]
                except Exception as e:
                    logger.warning(f"AI search failed: {e}")
        
        cover_url = book_data.get("cover_url")
        if cover_url and (cover_url.startswith("http://") or cover_url.startswith("https://")):
            external_cover_url = cover_url
        return book_data, external_cover_url

    async def delete_book(self, book_id: UUID, user_id: UUID | None = None) -> None:
        existing = await self._repo.get_by_id(book_id)
        if not existing:
            raise BookNotFoundException(book_id)
        if user_id is not None and existing.owner_id != user_id:
            raise NotBookOwnerException()
        deleted = await self._repo.delete(book_id)
        if not deleted:
            raise BookNotFoundException(book_id)
        if user_id:
            logger.info(f"Book deleted: {book_id} by user {user_id}")

    async def list_books(self, skip: int = 0, limit: int = 100) -> list[BookResponse]:
        books = await self._repo.list_all(skip=skip, limit=limit)
        return [BookResponse.model_validate(b) for b in books]

    async def get_user_books(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[BookResponse]:
        books = await self._repo.get_by_owner(user_id, skip=skip, limit=limit)
        return [BookResponse.model_validate(b) for b in books]

    async def get_community_books(
        self, 
        user_id: UUID | None, 
        skip: int = 0, 
        limit: int = 100,
        status: str | None = None,
        search: str | None = None,
        author: str | None = None
    ) -> list[CommunityBookResponse]:
        book_tuples = await self._repo.get_available_for_community(
            exclude_user_id=user_id,
            skip=skip, 
            limit=limit,
            status=status,
            search=search,
            author=author
        )
        result = []
        for book, user_book, owner in book_tuples:
            result.append(CommunityBookResponse(
                id=book.id,
                isbn=book.isbn,
                title=book.title,
                author=book.author,
                description=book.description,
                cover_url=f"/covers/{book.isbn}.jpg" if book.isbn else None,
                publisher=book.publisher,
                publication_year=book.publication_year,
                page_count=book.page_count,
                language=book.language,
                genre=book.genre,
                owner_id=user_book.user_id,
                owner=OwnerInfo(id=owner.id, first_name=owner.first_name, last_name=owner.last_name, location=owner.location),
                status=user_book.status,
                condition=user_book.condition,
                is_lendable=user_book.is_lendable,
                created_at=book.created_at,
                updated_at=book.updated_at,
            ))
        return result
    
    async def count_community_books(self, user_id: UUID | None, status: str | None = None, search: str | None = None, author: str | None = None) -> int:
        return await self._repo.count_available_for_community(exclude_user_id=user_id, status=status, search=search, author=author)

    async def search_books(self, query: str, filters: dict) -> list[BookResponse]:
        books = await self._repo.search(query, filters)
        return [BookResponse.model_validate(b) for b in books]

    async def add_book(self, user_id: UUID, data: BookCreate) -> BookResponse:
        book_data = data.model_dump()
        book_data["id"] = uuid.uuid4()
        book_data["owner_id"] = user_id
        book_data["status"] = "available"
        book_data["available"] = True
        
        db_book = await self._repo.create_book_from_dict(book_data)
        logger.info(f"Book created: {db_book.id} by user {user_id}")
        
        if self._vector_sync:
            await self._vector_sync(db_book.id, db_book.title, db_book.author, db_book.description)
        return BookResponse.model_validate(db_book)

    async def toggle_lendable(self, book_id: UUID, user_id: UUID, is_lendable: bool) -> BookResponse:
        existing = await self._repo.get_by_id(book_id)
        if not existing:
            raise BookNotFoundException(book_id)
        if existing.owner_id != user_id:
            raise NotBookOwnerException()
        
        update_data = BookUpdate(is_lendable=is_lendable)
        updated = await self._repo.update(book_id, update_data)
        
        logger.info(f"Book lendable status updated: {book_id} to {is_lendable} by user {user_id}")
        
        return BookResponse.model_validate(updated)

    async def get_by_isbn(self, isbn: str) -> BookResponse | None:
        """Get book by ISBN."""
        book = await self._repo.get_by_isbn(isbn)
        if not book:
            return None
        return BookResponse.model_validate(book)

    async def search(
        self,
        query: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[BookResponse], int]:
        """Search books with filters and pagination."""
        books, total = await self._repo.search(
            query=query,
            author=author,
            genre=genre,
            skip=skip,
            limit=limit
        )
        return [BookResponse.model_validate(b) for b in books], total
