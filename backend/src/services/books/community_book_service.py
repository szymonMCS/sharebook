import logging
from uuid import UUID
from typing import Optional, List
from src.services.interfaces.books import ICommunityBookService
from database.interfaces import IUserBookRepository, IBookRepository, IUserRepository
from src.schemas.book import CommunityBookResponse, OwnerInfo

logger = logging.getLogger(__name__)


class CommunityBookService(ICommunityBookService):
    def __init__(
        self,
        user_book_repo: IUserBookRepository,
        book_repo: IBookRepository,
        user_repo: IUserRepository
    ):
        self._user_book_repo = user_book_repo
        self._book_repo = book_repo
        self._user_repo = user_repo

    async def get_community_books(
        self,
        exclude_user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[CommunityBookResponse], int]:
        results = await self._user_book_repo.get_available_for_community(
            exclude_user_id=exclude_user_id,
            status=status,
            search=search,
            author=author,
            skip=skip,
            limit=limit
        )

        total = await self._user_book_repo.count_available_for_community(
            exclude_user_id=exclude_user_id,
            status=status,
            search=search,
            author=author
        )

        responses = []
        for book, user_book, owner in results:
            responses.append(CommunityBookResponse(
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
                owner=OwnerInfo(
                    id=owner.id,
                    first_name=owner.first_name,
                    last_name=owner.last_name,
                    location=owner.location
                ),
                status=user_book.status,
                condition=user_book.condition,
                is_lendable=user_book.is_lendable,
                created_at=book.created_at,
                updated_at=book.updated_at
            ))

        return responses, total
