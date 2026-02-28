import uuid
from typing import Optional, List
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import IUserBookRepository
from database.models import UserBook, Book, User


class UserBookRepository(IUserBookRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, id: uuid.UUID) -> Optional[UserBook]:
        result = await self._db.execute(
            select(UserBook).where(UserBook.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_book(self, user_id: uuid.UUID, book_id: uuid.UUID) -> Optional[UserBook]:
        result = await self._db.execute(
            select(UserBook).where(
                and_(UserBook.user_id == user_id, UserBook.book_id == book_id)
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: uuid.UUID,
        book_id: uuid.UUID,
        status: str = "available",
        condition: Optional[str] = None,
        is_lendable: bool = True
    ) -> UserBook:
        user_book = UserBook(
            user_id=user_id,
            book_id=book_id,
            status=status,
            condition=condition,
            is_lendable=is_lendable
        )
        self._db.add(user_book)
        await self._db.commit()
        await self._db.refresh(user_book)
        return user_book

    async def update(
        self,
        id: uuid.UUID,
        status: Optional[str] = None,
        condition: Optional[str] = None,
        is_lendable: Optional[bool] = None
    ) -> Optional[UserBook]:
        user_book = await self.get_by_id(id)
        if not user_book:
            return None

        if status is not None:
            user_book.status = status
        if condition is not None:
            user_book.condition = condition
        if is_lendable is not None:
            user_book.is_lendable = is_lendable

        await self._db.commit()
        await self._db.refresh(user_book)
        return user_book

    async def delete(self, id: uuid.UUID) -> bool:
        user_book = await self.get_by_id(id)
        if not user_book:
            return False

        await self._db.delete(user_book)
        await self._db.commit()
        return True

    async def get_user_library(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[tuple[UserBook, Book]]:
        result = await self._db.execute(
            select(UserBook, Book)
            .join(Book, UserBook.book_id == Book.id)
            .where(UserBook.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.all()

    def _build_community_subquery(self, status: Optional[str] = None):
        subquery_base = (
            select(
                UserBook.book_id,
                func.min(UserBook.id).label('first_user_book_id')
            )
            .where(UserBook.is_lendable == True)
        )

        status_filter = None if status == 'all' else (status if status else "available")
        if status_filter:
            subquery_base = subquery_base.where(UserBook.status == status_filter)

        return subquery_base.group_by(UserBook.book_id).subquery()

    def _apply_community_filters(self, query, subquery, exclude_user_id, search, author):
        query = (
            query
            .join(UserBook, Book.id == UserBook.book_id)
            .join(User, UserBook.user_id == User.id)
            .join(subquery,
                (UserBook.book_id == subquery.c.book_id) &
                (UserBook.id == subquery.c.first_user_book_id)
            )
        )

        if exclude_user_id:
            query = query.where(UserBook.user_id != exclude_user_id)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.description.ilike(search_term)
                )
            )

        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))

        return query

    async def get_available_for_community(
        self,
        exclude_user_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[tuple[Book, UserBook, User]]:
        subquery = self._build_community_subquery(status)
        query = select(Book, UserBook, User)
        query = self._apply_community_filters(query, subquery, exclude_user_id, search, author)
        query = query.offset(skip).limit(limit)
        
        result = await self._db.execute(query)
        return result.all()

    async def count_available_for_community(
        self,
        exclude_user_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None
    ) -> int:
        subquery = self._build_community_subquery(status)
        query = select(func.count(Book.id))
        query = self._apply_community_filters(query, subquery, exclude_user_id, search, author)
        
        result = await self._db.execute(query)
        return result.scalar() or 0
