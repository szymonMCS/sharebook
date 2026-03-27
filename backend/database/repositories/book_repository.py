import uuid
from datetime import datetime
from typing import Optional, List, Any, Tuple
from sqlalchemy import select, or_, func, update as sa_update, String
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Book, UserBook, User, Loan
from database.interfaces import IBookRepository


class BookRepository(IBookRepository):
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def get(self, book_id: uuid.UUID) -> Optional[Book]:
        return await self._db.get(Book, book_id)
    
    async def get_by_id(self, book_id: uuid.UUID) -> Optional[Book]:
        return await self._db.get(Book, book_id)
    
    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(select(Book).where(Book.isbn == isbn))
        return result.scalar_one_or_none()
    
    async def get_by_isbn_for_update(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(select(Book).where(Book.isbn == isbn).with_for_update())
        return result.scalar_one_or_none()
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[Book]:
        result = await self._db.execute(select(Book).offset(skip).limit(limit))
        return list(result.scalars().all())
    
    async def exists(self, book_id: uuid.UUID) -> bool:
        result = await self._db.execute(select(func.count()).where(Book.id == book_id))
        count = result.scalar()
        return count > 0 if count is not None else False
    
    async def get_by_id_with_owner(self, book_id: uuid.UUID) -> Optional[tuple[Book, UserBook, User]]:
        result = await self._db.execute(
            select(Book, UserBook, User)
            .join(UserBook, Book.id == UserBook.book_id)
            .join(User, UserBook.user_id == User.id)
            .where(Book.id == book_id)
            .limit(1)
        )
        row = result.first()
        if row is None:
            return None
        return (row[0], row[1], row[2])
    
    async def search(self, query: str, skip: int = 0, limit: int = 20, filters: Optional[dict] = None) -> Tuple[List[Book], int]:
        stmt = select(Book)
        count_stmt = select(func.count(Book.id))
        
        conditions = []
        if query:
            search_filter = or_(Book.title.ilike(f"%{query}%"), Book.authors.ilike(f"%{query}%"), Book.isbn.ilike(f"%{query}%"))
            conditions.append(search_filter)
        
        if filters:
            if "author" in filters:
                conditions.append(Book.authors.ilike(f"%{filters['author']}%"))
            if "genre" in filters:
                conditions.append(Book.categories.ilike(f"%{filters['genre']}%"))
        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)
        
        count_result = await self._db.execute(count_stmt)
        total = count_result.scalar() or 0
        stmt = stmt.offset(skip).limit(limit)
        result = await self._db.execute(stmt)
        books = list(result.scalars().all())
        return books, total
    
    async def create(self, book_data: dict) -> Book:
        book = Book(**book_data)
        self._db.add(book)
        await self._db.commit()
        await self._db.refresh(book)
        return book
    
    async def update(self, book_id: uuid.UUID, update_data: dict) -> Optional[Book]:
        result = await self._db.execute(sa_update(Book).where(Book.id == book_id).values(**update_data).returning(Book))
        await self._db.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, book_id: uuid.UUID) -> bool:
        book = await self.get(book_id)
        if not book:
            return False
        await self._db.delete(book)
        await self._db.commit()
        return True
    
    async def get_available_for_community(
        self,
        exclude_user_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Any]:
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["search"] = search
        if author:
            filters["author"] = author
        items, _ = await self.get_community_books(exclude_user_id=exclude_user_id, skip=skip, limit=limit, filters=filters)
        return items
    
    async def count_available_for_community(
        self,
        exclude_user_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None
    ) -> int:
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["search"] = search
        if author:
            filters["author"] = author
        _, total = await self.get_community_books(exclude_user_id=exclude_user_id, skip=0, limit=1, filters=filters)
        return total
    
    async def get_community_books(self, exclude_user_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 20, filters: Optional[dict] = None) -> Tuple[List[Any], int]:
        import logging
        logger = logging.getLogger(__name__)
        
        status_filter = None
        if filters and "status" in filters and filters["status"]:
            if filters["status"] != "all":
                status_filter = filters["status"]
        
        logger.info(f"[REPO] get_community_books: exclude_user_id={exclude_user_id}, status_filter={status_filter}, filters={filters}")
        
        stmt = select(Book, UserBook, User).join(UserBook, Book.id == UserBook.book_id).join(User, UserBook.user_id == User.id)
        count_stmt = select(func.count(Book.id)).join(UserBook, Book.id == UserBook.book_id)
        
        if status_filter:
            stmt = stmt.where(UserBook.status == status_filter)
            count_stmt = count_stmt.where(UserBook.status == status_filter)
        
        if exclude_user_id:
            stmt = stmt.where(UserBook.user_id != exclude_user_id)
            count_stmt = count_stmt.where(UserBook.user_id != exclude_user_id)
        
        if filters:
            if "search" in filters and filters["search"]:
                search = f"%{filters['search']}%"
                stmt = stmt.where(or_(Book.title.ilike(search), Book.author.ilike(search)))
                count_stmt = count_stmt.where(or_(Book.title.ilike(search), Book.author.ilike(search)))
            if "author" in filters and filters["author"]:
                author_filter = Book.author.ilike(f"%{filters['author']}%")
                stmt = stmt.where(author_filter)
                count_stmt = count_stmt.where(author_filter)
        
        count_result = await self._db.execute(count_stmt)
        total = count_result.scalar() or 0
        stmt = stmt.offset(skip).limit(limit)
        result = await self._db.execute(stmt)
        items = list(result.all())
        return items, total
    
    async def count_all(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Book))
        return result.scalar() or 0
    
    async def get_recent_books(self, limit: int = 10) -> List[Book]:
        result = await self._db.execute(select(Book).order_by(Book.created_at.desc()).limit(limit))
        return list(result.scalars().all())
    
    async def get_top_rated_books(self, limit: int = 10) -> List[Book]:
        result = await self._db.execute(select(Book).where(Book.average_rating.isnot(None)).order_by(Book.average_rating.desc()).limit(limit))
        return list(result.scalars().all())
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Book]:
        return await self.get_multi(skip, limit)
    
    async def create_book_from_dict(self, book_data: dict) -> Book:
        return await self.create(book_data)
    
    async def get_daily_additions(self, days: int = 30) -> List[dict]:
        from datetime import timezone, timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)
        from database.models import UserBook
        stmt = (
            select(func.date(UserBook.added_at).label("date"), func.count().label("count"))
            .where(UserBook.added_at >= since)
            .group_by(func.date(UserBook.added_at))
            .order_by(func.date(UserBook.added_at))
        )
        result = await self._db.execute(stmt)
        return [{"date": str(row.date), "count": row.count} for row in result.all()]
    
    async def get_popular_books(self, days: int = 30, limit: int = 10) -> List[dict]:
        from datetime import timezone, timedelta
        from database.models import Loan, UserBook
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(Book, func.count(Loan.id).label("loan_count"))
            .join(UserBook, UserBook.book_id == Book.id)
            .join(Loan, Loan.user_book_id == UserBook.id)
            .where(Loan.created_at >= since)
            .group_by(Book.id)
            .order_by(func.count(Loan.id).desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return [
            {
                "id": str(row.Book.id),
                "title": row.Book.title,
                "author": row.Book.author,
                "loan_count": row.loan_count
            }
            for row in result.all()
        ]
    
    async def get_by_owner(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Book]:
        from database.models import UserBook
        stmt = (
            select(Book)
            .join(UserBook, UserBook.book_id == Book.id)
            .where(UserBook.user_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_multi_with_search(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Tuple[List[Book], int]:
        query = select(Book)
        if search:
            query = query.where(
                (Book.title.ilike(f"%{search}%")) |
                (Book.author.ilike(f"%{search}%")) |
                (Book.isbn.ilike(f"%{search}%"))
            )
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self._db.execute(count_query)).scalar() or 0
        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all()), total
    
    async def get_book_stats(self, book_id: uuid.UUID) -> dict:
        from database.models import UserBook, Loan
        
        owners_count = await self._db.execute(select(func.count()).where(UserBook.book_id == book_id))
        active_loans = await self._db.execute(
            select(func.count())
            .select_from(Loan)
            .join(UserBook, Loan.user_book_id == UserBook.id)
            .where(UserBook.book_id == book_id, Loan.status == "active")
        )
        total_loans = await self._db.execute(
            select(func.count())
            .select_from(Loan)
            .join(UserBook, Loan.user_book_id == UserBook.id)
            .where(UserBook.book_id == book_id)
        )
        return {
            "owners_count": owners_count.scalar() or 0,
            "active_loans": active_loans.scalar() or 0,
            "total_loans": total_loans.scalar() or 0,
        }
    
    async def count_books(self) -> int:
        return await self.count_all()
    
    async def count_new_since(self, since: datetime) -> int:
        result = await self._db.execute(select(func.count()).select_from(Book).where(Book.created_at >= since))
        return result.scalar() or 0
    
    async def get_multi_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        author: Optional[str] = None,
        category: Optional[str] = None
    ) -> Tuple[List[Book], int]:
        query = select(Book)
        
        if search:
            query = query.where((Book.title.ilike(f"%{search}%")) |(Book.authors.ilike(f"%{search}%")))
        if author:
            query = query.where(Book.authors.ilike(f"%{author}%"))
        if category:
            query = query.where(Book.categories.ilike(f"%{category}%"))
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self._db.execute(count_query)).scalar() or 0
        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all()), total
