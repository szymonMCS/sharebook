import logging
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.interfaces.books import ILibraryManagementService
from database.interfaces import IUserBookRepository, IBookRepository
from src.schemas.book import UserBookResponse, BookStatus, BookCondition, BookResponse
from src.core.exceptions import BookNotFoundException, NotBookOwnerException, InvalidBookStatusException
from src.core.validators import validate_isbn, normalize_isbn
from src.core.constants import PLACEHOLDER_TITLE
from src.schemas.book import BookCondition, BookStatus

logger = logging.getLogger(__name__)


class LibraryManagementService(ILibraryManagementService):
    def __init__(
        self,
        user_book_repo: IUserBookRepository,
        book_repo: IBookRepository,
        db: AsyncSession
    ):
        self._user_book_repo = user_book_repo
        self._book_repo = book_repo
        self._db = db

    async def add_book_to_library(self, user_id: UUID, isbn: str, condition: str) -> UserBookResponse:
        is_valid, error = validate_isbn(isbn)
        if not is_valid:
            raise ValueError(f"Invalid ISBN: {error}")
        
        normalized_isbn = normalize_isbn(isbn)
        async with self._db.begin():
            book = await self._book_repo.get_by_isbn(normalized_isbn)
            if not book:
                book = await self._book_repo.create(
                    isbn=normalized_isbn,
                    title=PLACEHOLDER_TITLE,
                    author="",
                    description="",
                    language="pl"
                )
                logger.info(f"Created placeholder book in catalog: {book.id}")

            if condition not in list(BookCondition):
                raise InvalidBookStatusException(f"Invalid condition: {condition}. Must be one of: {', '.join(c.value for c in BookCondition)}")
            
            user_book = await self._user_book_repo.create(
                user_id=user_id,
                book_id=book.id,
                status=BookStatus.AVAILABLE,
                condition=condition,
                is_lendable=True
            )
            logger.info(f"Book {book.id} added to user {user_id} library as new copy")
            return await self._get_user_book_response(user_book)

    async def get_library(self, user_id: UUID, skip: int = 0, limit: int = 100) -> tuple[List[UserBookResponse], int]:
        user_books = await self._user_book_repo.get_user_library_with_books(user_id, skip, limit)
        total = await self._user_book_repo.count_user_library(user_id)
        responses = []
        for user_book in user_books:
            responses.append(self._create_user_book_response(user_book, user_book.book))
        return responses, total

    async def get_library_item(self, user_id: UUID, user_book_id: UUID) -> Optional[UserBookResponse]:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        self._assert_ownership(user_book, user_id)
        return await self._get_user_book_response(user_book)

    async def remove_from_library(self, user_id: UUID, user_book_id: UUID) -> bool:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        self._assert_ownership(user_book, user_id)

        if user_book.status in [BookStatus.BORROWED, BookStatus.LENT]:
            raise InvalidBookStatusException("Cannot remove borrowed or lent book")

        success = await self._user_book_repo.delete(user_book_id)
        if success:
            logger.info(f"Book {user_book_id} removed from user {user_id} library")
        return success

    async def update_lendable_status(self, user_id: UUID, user_book_id: UUID, is_lendable: bool) -> UserBookResponse:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        self._assert_ownership(user_book, user_id)

        updated = await self._user_book_repo.update(
            user_book_id,
            is_lendable=is_lendable
        )
        logger.info(f"Book {user_book_id} lendable status changed to {is_lendable}")
        return await self._get_user_book_response(updated)

    async def update_status(self, user_id: UUID, user_book_id: UUID, status: str) -> UserBookResponse:
        user_book = await self._user_book_repo.get_by_id(user_book_id)
        self._assert_ownership(user_book, user_id)

        updated = await self._user_book_repo.update(user_book_id, status=status)
        logger.info(f"Book {user_book_id} status changed to {status}")
        return await self._get_user_book_response(updated)

    def _assert_ownership(self, user_book, user_id: UUID) -> None:
        """Assert that user owns the book. Raises NotBookOwnerException if not."""
        if not user_book:
            raise BookNotFoundException(user_book.id if hasattr(user_book, 'id') else None)
        if user_book.user_id != user_id:
            raise NotBookOwnerException()

    async def _get_user_book_response(self, user_book) -> UserBookResponse:
        book = await self._book_repo.get_by_id(user_book.book_id)
        return self._create_user_book_response(user_book, book)

    def _create_user_book_response(self, user_book, book) -> UserBookResponse:
        return UserBookResponse(
            id=user_book.id,
            status=user_book.status,
            condition=user_book.condition,
            is_lendable=user_book.is_lendable,
            book=BookResponse.model_validate(book),
            added_at=user_book.added_at,
            updated_at=user_book.updated_at
        )
