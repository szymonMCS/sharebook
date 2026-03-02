import uuid
from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import IBookRepository
from database.models import Book


class BookRepository(IBookRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, id: uuid.UUID) -> Optional[Book]:
        result = await self._db.execute(
            select(Book).where(Book.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(
            select(Book).where(Book.isbn == isbn)
        )
        return result.scalar_one_or_none()

    async def create(self, isbn: str, title: str, **kwargs) -> Book:
        book = Book(isbn=isbn, title=title, **kwargs)
        self._db.add(book)
        await self._db.commit()
        await self._db.refresh(book)
        return book

    async def update(self, id: uuid.UUID, book_data: dict) -> Optional[Book]:
        book = await self.get_by_id(id)
        if not book:
            return None

        if hasattr(book_data, 'model_dump'):
            data = book_data.model_dump(exclude_unset=True)
        else:
            data = book_data

        for key, value in data.items():
            if hasattr(book, key) and value is not None:
                setattr(book, key, value)

        await self._db.commit()
        await self._db.refresh(book)
        return book

    async def delete(self, id: uuid.UUID) -> bool:
        book = await self.get_by_id(id)
        if not book:
            return False

        await self._db.delete(book)
        await self._db.commit()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Book]:
        result = await self._db.execute(
            select(Book).offset(skip).limit(limit)
        )
        return result.scalars().all()

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
            search_filter = or_(
                Book.title.ilike(f"%{query}%"),
                Book.author.ilike(f"%{query}%"),
                Book.description.ilike(f"%{query}%")
            )
            base_query = base_query.where(search_filter)

        if author:
            base_query = base_query.where(Book.author.ilike(f"%{author}%"))

        if genre:
            base_query = base_query.where(Book.genre.ilike(f"%{genre}%"))

        count_result = await self._db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar() or 0

        result = await self._db.execute(
            base_query.offset(skip).limit(limit)
        )
        books = result.scalars().all()

        return list(books), total
