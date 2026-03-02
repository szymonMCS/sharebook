import logging
from uuid import UUID
from typing import Optional, List
from src.services.interfaces import ILibraryManagementService
from database.interfaces import IUserBookRepository, IBookRepository
from src.schemas.book import UserBookResponse
from src.core.exceptions import BookNotFoundException, NotBookOwnerException

logger = logging.getLogger(__name__)


class LibraryManagementService(ILibraryManagementService):
    def __init__(
        self,
        user_book_repo: IUserBookRepository,
        book_repo: IBookRepository
    ):
        self._user_book_repo = user_book_repo
        self._book_repo = book_repo

    async def add_book_to_library(self, user_id: UUID, isbn: str, condition: str) -> UserBookResponse:
        book = await self._book_repo.get_by_isbn(isbn)
        if not book:
            book = await self._book_repo.create(
                isbn=isbn,
                title="Wczytywanie...",
                author="",
                description="",
                language="pl"
            )
            logger.info(f"Created placeholder book in catalog: {book.id}")

        user_book = await self._user_book_repo.create(
            user_id=user_id,
            book_id=book.id,
            status="available",
            condition=condition,
            is_lendable=True
        )
        logger.info(f"Book {book.id} added to user {user_id} library as new copy")
        return await self._get_user_book_response(user_book)

    async def get_library(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[UserBookResponse]:
        results = await self._user_book_repo.get_user_library(user_id, skip, limit)
        responses = []
        for user_book, book in results:
            responses.append(self._create_user_book_response(user_book, book))
        return responses

    async def get_library_item(self, user_id: UUID, user_book_id: UUID) -> Optional[UserBookResponse]:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        if not user_book or user_book.user_id != user_id:
            return None
        return await self._get_user_book_response(user_book)

    async def remove_from_library(self, user_id: UUID, user_book_id: UUID) -> bool:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        if not user_book:
            raise BookNotFoundException(user_book_id)

        if user_book.user_id != user_id:
            raise NotBookOwnerException()

        if user_book.status in ["borrowed", "lent"]:
            raise ValueError("Cannot remove borrowed or lent book")

        success = await self._user_book_repo.delete(user_book_id)
        if success:
            logger.info(f"Book {user_book_id} removed from user {user_id} library")
        return success

    async def update_lendable_status(self, user_id: UUID, user_book_id: UUID, is_lendable: bool) -> UserBookResponse:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        if not user_book:
            raise BookNotFoundException(user_book_id)

        if user_book.user_id != user_id:
            raise NotBookOwnerException()

        updated = await self._user_book_repo.update(
            user_book_id,
            is_lendable=is_lendable
        )
        logger.info(f"Book {user_book_id} lendable status changed to {is_lendable}")
        return await self._get_user_book_response(updated)

    async def update_status(self, user_id: UUID, user_book_id: UUID, status: str) -> UserBookResponse:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        if not user_book:
            raise BookNotFoundException(user_book_id)

        if user_book.user_id != user_id:
            raise NotBookOwnerException()

        updated = await self._user_book_repo.update(user_book_id, status=status)
        logger.info(f"Book {user_book_id} status changed to {status}")
        return await self._get_user_book_response(updated)

    async def _get_user_book_response(self, user_book) -> UserBookResponse:
        book = await self._book_repo.get_by_id(user_book.book_id)
        return self._create_user_book_response(user_book, book)

    def _create_user_book_response(self, user_book, book) -> UserBookResponse:
        return UserBookResponse(
            id=user_book.id,
            status=user_book.status,
            condition=user_book.condition,
            is_lendable=user_book.is_lendable,
            book={
                "id": book.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "publisher": book.publisher,
                "publication_year": book.publication_year,
                "page_count": book.page_count,
                "language": book.language,
                "genre": book.genre,
                "cover_path": book.cover_path,
                "created_at": book.created_at,
                "updated_at": book.updated_at
            },
            added_at=user_book.added_at,
            updated_at=user_book.updated_at
        )
