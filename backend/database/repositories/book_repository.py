import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, or_, func, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import IBookRepository
from database.models import Book, UserBook, Loan


class BookRepository(IBookRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    def _escape_like_pattern(self, pattern: str) -> str:
        return (
            pattern
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )

    async def get_by_id(self, id: uuid.UUID) -> Optional[Book]:
        result = await self._db.execute(select(Book).where(Book.id == id))
        return result.scalar_one_or_none()

    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(select(Book).where(Book.isbn == isbn))
        return result.scalar_one_or_none()

    async def get_by_isbn_for_update(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(select(Book).where(Book.isbn == isbn).with_for_update())
        return result.scalar_one_or_none()

    async def create(self, isbn: str, title: str, **kwargs) -> Book:
        book = Book(isbn=isbn, title=title, **kwargs)
        self._db.add(book)
        await self._db.commit()
        await self._db.refresh(book)
        return book

    async def update(self, id: uuid.UUID, book_data: dict) -> Optional[Book]:
        if hasattr(book_data, 'model_dump'):
            data = book_data.model_dump(exclude_unset=True)
        else:
            data = book_data

        result = await self._db.execute(
            sa_update(Book)
            .where(Book.id == id)
            .values(**data)
            .returning(Book)
        )
        await self._db.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: uuid.UUID) -> bool:
        book = await self.get_by_id(id)
        if not book:
            return False

        await self._db.delete(book)
        await self._db.commit()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Book]:
        result = await self._db.execute(select(Book).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> tuple[List[Book], int]:
        count_result = await self._db.execute(select(func.count()).select_from(Book))
        total = count_result.scalar() or 0
        result = await self._db.execute(select(Book).offset(skip).limit(limit))
        books = list(result.scalars().all())
        return books, total

    async def search(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Book], int]:
        base_query = select(Book)

        if query:
            search_pattern = f"%{self._escape_like_pattern(query)}%"
            search_filter = or_(
                Book.title.ilike(search_pattern, escape="\\"),
                Book.author.ilike(search_pattern, escape="\\"),
                Book.description.ilike(search_pattern, escape="\\")
            )
            base_query = base_query.where(search_filter)

        if author:
            author_pattern = f"%{self._escape_like_pattern(author)}%"
            base_query = base_query.where(Book.author.ilike(author_pattern, escape="\\"))

        if genre:
            genre_pattern = f"%{self._escape_like_pattern(genre)}%"
            base_query = base_query.where(Book.genre.ilike(genre_pattern, escape="\\"))

        count_result = await self._db.execute(select(func.count()).select_from(base_query.subquery()))
        total = count_result.scalar() or 0
        result = await self._db.execute(base_query.offset(skip).limit(limit))
        books = result.scalars().all()
        return list(books), total

    async def get_multi_with_search(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[List[Book], int]:
        query = select(Book)
        count_query = select(func.count()).select_from(Book)
        
        if search:
            search_pattern = f"%{self._escape_like_pattern(search)}%"
            search_filter = or_(
                Book.title.ilike(search_pattern, escape="\\"),
                Book.author.ilike(search_pattern, escape="\\"),
                Book.isbn.ilike(search_pattern, escape="\\")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        query = query.order_by(Book.created_at.desc())
        
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0
        
        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        books = list(result.scalars().all())
        return books, total

    async def count_all(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Book))
        return result.scalar() or 0

    async def count_new_since(self, since: datetime) -> int:
        result = await self._db.execute(select(func.count()).select_from(Book).where(Book.created_at >= since))
        return result.scalar() or 0

    async def get_book_stats(self, book_id: uuid.UUID) -> dict:
        owners_count = await self._db.scalar(select(func.count(func.distinct(UserBook.user_id))).where(UserBook.book_id == book_id))
        copies_count = await self._db.scalar(select(func.count()).select_from(UserBook).where(UserBook.book_id == book_id))
        loans_count = await self._db.scalar(select(func.count()).select_from(Loan).join(UserBook, Loan.user_book_id == UserBook.id).where(UserBook.book_id == book_id))
        active_loans_count = await self._db.scalar(select(func.count()).select_from(Loan).join(UserBook, Loan.user_book_id == UserBook.id).where(
                UserBook.book_id == book_id,
                Loan.status == "active"
            )
        )
        return {
            "owners_count": owners_count or 0,
            "copies_count": copies_count or 0,
            "loans_count": loans_count or 0,
            "active_loans_count": active_loans_count or 0
        }

    async def get_popular_books(self, days: int, limit: int = 10) -> List[dict]:
        from datetime import timezone, timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(Book.id, Book.title, Book.author, func.count(Loan.id).label("loan_count"))
            .join(Loan, Loan.user_book_id == Book.id)
            .where(Loan.created_at >= since)
            .group_by(Book.id, Book.title, Book.author)
            .order_by(func.count(Loan.id).desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return [
            {
                "id": str(row.id),
                "title": row.title,
                "author": row.author,
                "loan_count": row.loan_count
            }
            for row in result.all()
        ]

    async def get_daily_additions(self, days: int) -> List[dict]:
        from datetime import timezone, timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(func.date(Book.created_at).label("date"), func.count().label("count"))
            .where(Book.created_at >= since)
            .group_by(func.date(Book.created_at))
            .order_by(func.date(Book.created_at))
        )
        result = await self._db.execute(stmt)
        return [{"date": str(row.date), "count": row.count} for row in result.all()]
