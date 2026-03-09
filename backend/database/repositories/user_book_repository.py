import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models import UserBook, Book, User
from database.interfaces import IUserBookRepository


class UserBookRepository(IUserBookRepository):
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def get_by_id(self, user_book_id: uuid.UUID) -> Optional[UserBook]:
        return await self._db.get(UserBook, user_book_id)
    
    async def get_by_id_for_update(self, user_book_id: uuid.UUID) -> Optional[UserBook]:
        result = await self._db.execute(select(UserBook).where(UserBook.id == user_book_id).with_for_update())
        return result.scalar_one_or_none()
    
    async def get_by_user_and_book(self, user_id: uuid.UUID, book_id: uuid.UUID) -> Optional[UserBook]:
        result = await self._db.execute(select(UserBook).where(and_(UserBook.user_id == user_id, UserBook.book_id == book_id)))
        return result.scalar_one_or_none()
    
    async def get_by_book_id(self, book_id: uuid.UUID) -> Optional[UserBook]:
        result = await self._db.execute(select(UserBook).where(UserBook.book_id == book_id))
        return result.scalar_one_or_none()
    
    async def get_by_id_for_user(self, user_book_id: uuid.UUID, user_id: uuid.UUID) -> Optional[UserBook]:
        result = await self._db.execute(select(UserBook).where(and_(UserBook.id == user_book_id, UserBook.user_id == user_id)))
        return result.scalar_one_or_none()
    
    async def get_with_book(self, user_book_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Tuple[UserBook, Book]]:
        result = await self._db.execute(select(UserBook, Book).join(Book, UserBook.book_id == Book.id).where(and_(UserBook.id == user_book_id, UserBook.user_id == user_id)))
        return result.one_or_none()
    
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
        user_book_id: uuid.UUID,
        status: Optional[str] = None,
        condition: Optional[str] = None,
        is_lendable: Optional[bool] = None,
        commit: bool = True
    ) -> Optional[UserBook]:
        user_book = await self.get_by_id(user_book_id)
        if not user_book:
            return None

        if status is not None:
            user_book.status = status
        if condition is not None:
            user_book.condition = condition
        if is_lendable is not None:
            user_book.is_lendable = is_lendable

        if commit:
            await self._db.commit()
            await self._db.refresh(user_book)
        else:
            await self._db.flush()
            await self._db.refresh(user_book)
        return user_book
    
    async def update_with_lock(
        self,
        user_book_id: uuid.UUID,
        status: Optional[str] = None,
        condition: Optional[str] = None,
        is_lendable: Optional[bool] = None,
        commit: bool = True
    ) -> Optional[UserBook]:
        user_book = await self.get_by_id_for_update(user_book_id)
        if not user_book:
            return None

        if status is not None:
            user_book.status = status
        if condition is not None:
            user_book.condition = condition
        if is_lendable is not None:
            user_book.is_lendable = is_lendable

        if commit:
            await self._db.commit()
            await self._db.refresh(user_book)
        else:
            await self._db.flush()
            await self._db.refresh(user_book)
        return user_book
    
    async def update_status(self, user_book_id: uuid.UUID, status: str, commit: bool = True) -> Optional[UserBook]:
        user_book = await self.get_by_id(user_book_id)
        if not user_book:
            return None

        user_book.status = status

        if commit:
            await self._db.commit()
            await self._db.refresh(user_book)
        else:
            await self._db.flush()
            await self._db.refresh(user_book)
        return user_book
    
    async def toggle_lendable(self, user_book_id: uuid.UUID) -> Optional[UserBook]:
        user_book = await self.get_by_id(user_book_id)
        if user_book:
            user_book.is_lendable = not user_book.is_lendable
            await self._db.commit()
            await self._db.refresh(user_book)
            return user_book
        return None
    
    async def delete(self, user_book_id: uuid.UUID) -> bool:
        user_book = await self.get_by_id(user_book_id)
        if not user_book:
            return False
        await self._db.delete(user_book)
        await self._db.commit()
        return True
    
    async def remove_from_user(self, user_id: uuid.UUID, book_id: uuid.UUID) -> bool:
        user_book = await self.get_by_user_and_book(user_id, book_id)
        if user_book:
            await self._db.delete(user_book)
            await self._db.commit()
            return True
        return False
    
    async def get_user_library(self, user_id: uuid.UUID) -> List[Tuple[UserBook, Book]]:
        result = await self._db.execute(select(UserBook, Book).join(Book, UserBook.book_id == Book.id).where(UserBook.user_id == user_id))
        return result.all()
    
    async def get_user_library_with_books(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[UserBook]:
        result = await self._db.execute(
            select(UserBook)
            .options(selectinload(UserBook.book))
            .where(UserBook.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    def _build_community_subquery(self, status: Optional[str] = None):
        subquery_base = (
            select(UserBook.book_id, func.min(UserBook.id).label('first_user_book_id'))
            .where(UserBook.is_lendable.is_(True))
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
            .join(subquery,(UserBook.book_id == subquery.c.book_id) & (UserBook.id == subquery.c.first_user_book_id)
            )
        )

        if exclude_user_id:
            query = query.where(UserBook.user_id != exclude_user_id)

        if search:
            search_term = f"%{search}%"
            query = query.where(or_(Book.title.ilike(search_term), Book.author.ilike(search_term), Book.description.ilike(search_term)))

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
    ) -> List[Tuple[Book, UserBook, User]]:
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
    
    async def count_user_library(self, user_id: uuid.UUID) -> int:
        result = await self._db.execute(select(func.count()).where(UserBook.user_id == user_id))
        return result.scalar() or 0
    
    async def count_by_status(self, status: str) -> int:
        result = await self._db.execute(select(func.count()).where(UserBook.status == status))
        return result.scalar() or 0
    
    async def count_owners_for_book(self, book_id: uuid.UUID) -> int:
        result = await self._db.execute(select(func.count(func.distinct(UserBook.user_id))).where(UserBook.book_id == book_id))
        return result.scalar() or 0
    
    async def count_copies_for_book(self, book_id: uuid.UUID) -> int:
        result = await self._db.execute(select(func.count()).where(UserBook.book_id == book_id))
        return result.scalar() or 0
    
    async def get_owners_for_book(self, book_id: uuid.UUID) -> List[UserBook]:
        result = await self._db.execute(
            select(UserBook)
            .options(selectinload(UserBook.user))
            .where(UserBook.book_id == book_id)
            .order_by(UserBook.added_at.desc())
        )
        return list(result.scalars().all())
    
    async def count_borrowed_by_user(self, user_id: uuid.UUID) -> int:
        from database.models import Loan
        result = await self._db.execute(select(func.count()).select_from(Loan).where(Loan.borrower_id == user_id))
        return result.scalar() or 0

    async def count_lent_by_user(self, user_id: uuid.UUID) -> int:
        from database.models import Loan
        result = await self._db.execute(select(func.count()).select_from(Loan).where(Loan.lender_id == user_id))
        return result.scalar() or 0
