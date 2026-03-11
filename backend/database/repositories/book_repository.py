import uuid
from datetime import datetime
from typing import Optional, List, Any, Tuple
from sqlalchemy import select, or_, func, update as sa_update, String
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Book, UserBook, User, Loan
from database.interfaces import IBookRepository


class BookRepository(IBookRepository):
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def get_by_id(self, book_id: uuid.UUID) -> Optional[Book]:
        return await self._db.get(Book, book_id)
    
    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(select(Book).where(Book.isbn == isbn))
        return result.scalar_one_or_none()
    
    async def get_by_isbn_for_update(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(select(Book).where(Book.isbn == isbn).with_for_update())
        return result.scalar_one_or_none()
    
    async def get_by_id_with_owner(self, book_id: uuid.UUID) -> Optional[tuple[Book, UserBook, User]]:
        result = await self._db.execute(
            select(Book, UserBook, User)
            .join(UserBook, Book.id == UserBook.book_id)
            .join(User, UserBook.user_id == User.id)
            .where(Book.id == book_id)
            .limit(1)
        )
        return result.one_or_none()
    
    async def create(self, isbn: str, title: str, **kwargs) -> Book:
        book = Book(isbn=isbn, title=title, **kwargs)
        self._db.add(book)
        await self._db.commit()
        await self._db.refresh(book)
        return book
    
    async def create_book_from_dict(self, book_data: dict) -> Book:
        book = Book(**book_data)
        self._db.add(book)
        await self._db.commit()
        await self._db.refresh(book)
        return book
    
    async def update(self, book_id: uuid.UUID, book_data: Any) -> Optional[Book]:
        book = await self._db.get(Book, book_id)
        if not book:
            return None
        
        if hasattr(book_data, 'model_dump'):
            data = book_data.model_dump(exclude_unset=True)
        else:
            data = book_data
            
        for key, value in data.items():
            if hasattr(book, key):
                setattr(book, key, value)
        
        await self._db.commit()
        await self._db.refresh(book)
        return book
    
    async def update_cover_path(self, book_id: uuid.UUID, cover_path: str) -> None:
        book = await self._db.get(Book, book_id)
        if book:
            book.cover_url = cover_path
            await self._db.commit()
    
    async def delete(self, book_id: uuid.UUID) -> bool:
        book = await self._db.get(Book, book_id)
        if not book:
            return False
        
        await self._db.delete(book)
        await self._db.commit()
        return True
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Book]:
        result = await self._db.execute(select(Book).offset(skip).limit(limit))
        return list(result.scalars().all())
    
    async def get_all(self) -> List[Book]:
        result = await self._db.execute(select(Book))
        return list(result.scalars().all())
    
    async def get_by_owner(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Book]:
        result = await self._db.execute(
            select(Book)
            .join(UserBook, Book.id == UserBook.book_id)
            .where(UserBook.user_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> tuple[List[Book], int]:
        count_result = await self._db.execute(select(func.count()).select_from(Book))
        total = count_result.scalar() or 0
        result = await self._db.execute(select(Book).offset(skip).limit(limit))
        books = list(result.scalars().all())
        return books, total
    
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
        
        result = await self._db.execute(query.offset(skip).limit(limit))
        books = list(result.scalars().all())
        return books, total
    
    def _escape_like_pattern(self, pattern: str) -> str:
        return (
            pattern
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
    
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
    
    async def search_by_title(self, query: str) -> List[Book]:
        result = await self._db.execute(select(Book).where(Book.title.ilike(f"%{query}%")))
        return list(result.scalars().all())
    
    async def get_available_for_community(
        self, 
        exclude_user_id: Optional[uuid.UUID] = None, 
        skip: int = 0, 
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None
    ) -> List[tuple[Book, UserBook, User]]:
        # Only show these statuses in community (exclude unavailable and lent)
        allowed_statuses = ['available', 'reserved', 'borrowed']
        
        if status == 'all' or not status:
            status_filter = None  # Will filter by allowed_statuses below
        elif status in allowed_statuses:
            status_filter = status
        else:
            # Invalid status for community, return empty
            return []
        
        subquery_base = (
            select(UserBook.book_id, func.min(UserBook.id.cast(String)).label('first_user_book_id'))
            .where(UserBook.is_lendable.is_(True))
            .where(UserBook.status.in_(allowed_statuses))
        )
        
        if status_filter:
            subquery_base = subquery_base.where(UserBook.status == status_filter)
        
        subquery = subquery_base.group_by(UserBook.book_id).subquery()
        
        query = (
            select(Book, UserBook, User)
            .join(UserBook, Book.id == UserBook.book_id)
            .join(User, UserBook.user_id == User.id)
            .join(subquery, (UserBook.book_id == subquery.c.book_id) & (UserBook.id.cast(String) == subquery.c.first_user_book_id))
        )
        
        if exclude_user_id:
            query = query.where(UserBook.user_id != exclude_user_id)
        if search:
            search_term = f"%{search}%"
            query = query.where(or_(Book.title.ilike(search_term), Book.author.ilike(search_term), Book.description.ilike(search_term)))
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        
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
        # Only show these statuses in community (exclude unavailable and lent)
        allowed_statuses = ['available', 'reserved', 'borrowed']
        
        if status == 'all' or not status:
            status_filter = None
        elif status in allowed_statuses:
            status_filter = status
        else:
            return 0
        
        subquery_base = (
            select(UserBook.book_id, func.min(UserBook.id.cast(String)).label('first_user_book_id'))
            .where(UserBook.is_lendable.is_(True))
            .where(UserBook.status.in_(allowed_statuses))
        )
        
        if status_filter:
            subquery_base = subquery_base.where(UserBook.status == status_filter)
        
        subquery = subquery_base.group_by(UserBook.book_id).subquery()
        
        query = (
            select(func.count(Book.id))
            .join(UserBook, Book.id == UserBook.book_id)
            .join(User, UserBook.user_id == User.id)
            .join(subquery, 
                (UserBook.book_id == subquery.c.book_id) & 
                (UserBook.id.cast(String) == subquery.c.first_user_book_id)
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
        
        result = await self._db.execute(query)
        return result.scalar() or 0
    
    async def count_all(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Book))
        return result.scalar() or 0
    
    async def count_new_since(self, since: datetime) -> int:
        result = await self._db.execute(select(func.count()).select_from(Book).where(Book.created_at >= since))
        return result.scalar() or 0
    
    async def get_book_stats(self, book_id: uuid.UUID) -> dict:
        owners_count = await self._db.scalar(
            select(func.count(func.distinct(UserBook.user_id)))
            .where(UserBook.book_id == book_id)
        )
        copies_count = await self._db.scalar(
            select(func.count()).select_from(UserBook).where(UserBook.book_id == book_id)
        )
        loans_count = await self._db.scalar(
            select(func.count()).select_from(Loan)
            .join(UserBook, Loan.user_book_id == UserBook.id)
            .where(UserBook.book_id == book_id)
        )
        active_loans_count = await self._db.scalar(
            select(func.count()).select_from(Loan)
            .join(UserBook, Loan.user_book_id == UserBook.id)
            .where(
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
    
    async def get_community_books(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        skip = (page - 1) * per_page
        
        query = (select(Book, UserBook, User).join(UserBook, Book.id == UserBook.book_id).join(User, UserBook.user_id == User.id))
        
        if status and status != 'all':
            query = query.where(UserBook.status == status)
        
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
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.offset(skip).limit(per_page)
        result = await self._db.execute(query)
        results = result.all()
        
        seen_ids = set()
        books = []
        for book, user_book, owner in results:
            book_id_str = str(book.id)
            if book_id_str not in seen_ids:
                seen_ids.add(book_id_str)
                books.append({
                    "id": book_id_str,
                    "isbn": book.isbn,
                    "title": book.title,
                    "author": book.author,
                    "description": book.description,
                    "cover_url": f"/covers/{book.isbn}.jpg" if book.isbn else None,
                    "genre": book.genre,
                    "publication_year": book.publication_year,
                    "status": user_book.status,
                    "is_lendable": user_book.is_lendable,
                    "owner_id": str(owner.id),
                    "owner": {
                        "id": str(owner.id),
                        "first_name": owner.first_name or "",
                        "last_name": owner.last_name or "",
                        "location": owner.location
                    }
                })
        return books, total


    async def enrich_book(self, book_id: uuid.UUID, enrichment_data: dict) -> Optional[Book]:
        book = await self.get_by_id(book_id)
        if not book:
            return None
        
        for key, value in enrichment_data.items():
            if hasattr(book, key) and value is not None:
                setattr(book, key, value)
        
        await self._db.commit()
        await self._db.refresh(book)
        return book
    
    async def get_with_owners(self, book_id: uuid.UUID) -> Optional[Book]:
        result = await self._db.execute(
            select(Book)
            .where(Book.id == book_id)
            .options(
                selectinload(Book.user_books).selectinload(UserBook.user)
            )
        )
        return result.scalar_one_or_none()
