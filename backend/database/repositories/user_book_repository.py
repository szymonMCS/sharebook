from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.repositories.base import BaseRepository
from database.interfaces import IUserBookRepository
from database.models import UserBook, Book, Loan

if TYPE_CHECKING:
    from database.models import Book


class UserBookRepository(BaseRepository[UserBook], IUserBookRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(UserBook, db)
    
    async def get_by_id(self, user_book_id: UUID) -> Optional[UserBook]:
        return await self.get(user_book_id)
    
    async def get_by_user(self, user_id: UUID, status: Optional[str] = None) -> List[UserBook]:
        query = select(UserBook).where(UserBook.user_id == user_id)
        if status:
            query = query.where(UserBook.status == status)
        query = query.order_by(UserBook.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_book_and_user(self, book_id: UUID, user_id: UUID) -> Optional[UserBook]:
        result = await self._db.execute(select(UserBook).where(and_(UserBook.book_id == book_id, UserBook.user_id == user_id)))
        return result.scalar_one_or_none()
    
    async def get_by_id_with_relations(self, user_book_id: UUID) -> Optional[UserBook]:
        result = await self._db.execute(
            select(UserBook)
            .options(joinedload(UserBook.user), joinedload(UserBook.book))
            .where(UserBook.id == user_book_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_for_update(self, user_book_id: UUID) -> Optional[UserBook]:
        result = await self._db.execute(select(UserBook).where(UserBook.id == user_book_id).with_for_update())
        return result.scalar_one_or_none()
    
    async def update_status(self, user_book_id: UUID, status: str) -> Optional[UserBook]:
        user_book = await self.get(user_book_id)
        if not user_book:
            return None
        
        user_book.status = status
        await self._db.commit()
        await self._db.refresh(user_book)
        return user_book
    
    async def get_user_library(self, user_id: UUID, status: Optional[str] = None) -> List[tuple[UserBook, "Book"]]:
        query = (select(UserBook, Book).join(Book, UserBook.book_id == Book.id).where(UserBook.user_id == user_id))
        if status:
            query = query.where(UserBook.status == status)
        query = query.order_by(Book.title)
        result = await self._db.execute(query)
        return list(result.all())
    
    async def toggle_lendable(self, id: UUID) -> Optional[UserBook]:
        user_book = await self.get(id)
        if not user_book:
            return None
        user_book.is_lendable = not user_book.is_lendable
        await self._db.commit()
        await self._db.refresh(user_book)
        return user_book
    
    async def has_active_loan(self, user_book_id: UUID) -> bool:
        result = await self._db.execute(select(func.count()).where(and_(Loan.user_book_id == user_book_id, Loan.status.in_(["active", "overdue"]))))
        return result.scalar() > 0
    
    async def count_user_library(self, user_id: UUID) -> int:
        result = await self._db.execute(select(func.count()).where(UserBook.user_id == user_id))
        return result.scalar() or 0
    
    async def count_lent_by_user(self, user_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .join(Loan, UserBook.id == Loan.user_book_id)
            .where(UserBook.user_id == user_id, Loan.status == "active")
        )
        return result.scalar() or 0
    
    async def count_by_status(self, status: str) -> int:
        result = await self._db.execute(select(func.count()).where(UserBook.status == status))
        return result.scalar() or 0
    
    async def get_owners_for_book(self, book_id: UUID) -> List["User"]:
        from database.models import User
        result = await self._db.execute(
            select(User).distinct()
            .join(UserBook, User.id == UserBook.user_id)
            .where(UserBook.book_id == book_id)
        )
        return list(result.scalars().all())
    
    async def get_by_user_and_book(self, user_id: UUID, book_id: UUID) -> Optional[UserBook]:
        result = await self._db.execute(select(UserBook).where(UserBook.user_id == user_id, UserBook.book_id == book_id))
        return result.scalar_one_or_none()
    
    async def update(self, user_book_id: UUID, obj_in: dict) -> Optional[UserBook]:
        user_book = await self.get(user_book_id)
        if not user_book:
            return None
        for field, value in obj_in.items():
            setattr(user_book, field, value)
        await self._db.commit()
        await self._db.refresh(user_book)
        return user_book
