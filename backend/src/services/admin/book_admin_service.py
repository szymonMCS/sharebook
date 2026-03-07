import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Book, UserBook, Loan
from database.interfaces import IBookRepository
from src.core.exceptions import BookNotFoundException
from src.services.admin.interfaces import IBookAdminService, BookListResult

logger = logging.getLogger(__name__)


class BookHasActiveLoansException(Exception):
    def __init__(self, book_id: UUID, active_loans: int):
        self.book_id = book_id
        self.active_loans = active_loans
        super().__init__(f"Book {book_id} has {active_loans} active loans")


class BookAdminService(IBookAdminService):
    def __init__(self, db: AsyncSession, book_repo: Optional[IBookRepository] = None):
        self._db = db
        self._book_repo = book_repo
        
        if self._book_repo is None:
            from database.repositories.book_repository import BookRepository
            self._book_repo = BookRepository(db)
    
    async def list_books(self, page: int = 1, per_page: int = 20, search: Optional[str] = None, has_loans: Optional[bool] = None) -> BookListResult:
        skip = (page - 1) * per_page
        query = select(Book)
        
        if search:
            search_filter = or_(Book.title.ilike(f"%{search}%"), Book.author.ilike(f"%{search}%"), Book.isbn.ilike(f"%{search}%"))
            query = query.where(search_filter)
        
        query = query.order_by(Book.created_at.desc())
        count_query = select(func.count()).select_from(Book)
        if search:
            count_query = count_query.where(search_filter)
        
        total = await self._db.scalar(count_query)
        query = query.offset(skip).limit(per_page)
        result = await self._db.execute(query)
        books = result.scalars().all()
        data = []
        for book in books:
            owners_count = await self._db.scalar(select(func.count(func.distinct(UserBook.user_id))).where(UserBook.book_id == book.id))
            loans_count = await self._db.scalar(select(func.count()).select_from(Loan).join(UserBook, Loan.user_book_id == UserBook.id).where(UserBook.book_id == book.id))
            data.append({
                "id": str(book.id),
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "publisher": book.publisher,
                "publication_year": book.publication_year,
                "language": book.language,
                "genre": book.genre,
                "created_at": book.created_at.isoformat() if book.created_at else None,
                "updated_at": book.updated_at.isoformat() if book.updated_at else None,
                "stats": {
                    "owners_count": owners_count or 0,
                    "loans_count": loans_count or 0
                }
            })
        return BookListResult(
            data=data,
            total=total or 0,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page if per_page > 0 else 0
        )
    
    async def get_book_details(self, book_id: UUID) -> dict:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(str(book_id))
        
        owners_count = await self._db.scalar(select(func.count(func.distinct(UserBook.user_id))).where(UserBook.book_id == book_id))
        copies_count = await self._db.scalar(select(func.count()).select_from(UserBook).where(UserBook.book_id == book_id))
        loans_count = await self._db.scalar(select(func.count()).select_from(Loan).join(UserBook, Loan.user_book_id == UserBook.id).where(UserBook.book_id == book_id))
        active_loans_count = await self._db.scalar(select(func.count()).select_from(Loan).join(UserBook, Loan.user_book_id == UserBook.id).where(
                UserBook.book_id == book_id,
                Loan.status == "active"
            )
        )
        owners_stmt = (select(UserBook).where(UserBook.book_id == book_id).order_by(UserBook.added_at.desc()))
        owners_result = await self._db.execute(owners_stmt)
        user_books = owners_result.scalars().all()
        
        owners = []
        for ub in user_books:
            from database.models import User
            user_result = await self._db.execute(select(User).where(User.id == ub.user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                owners.append({
                    "user_book_id": str(ub.id),
                    "user_id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "status": ub.status,
                    "condition": ub.condition,
                    "is_lendable": ub.is_lendable,
                    "added_at": ub.added_at.isoformat() if ub.added_at else None
                })
        return {
            "id": str(book.id),
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "description": book.description,
            "publisher": book.publisher,
            "publication_year": book.publication_year,
            "page_count": book.page_count,
            "language": book.language,
            "genre": book.genre,
            "cover_url": book.cover_url,
            "created_at": book.created_at.isoformat() if book.created_at else None,
            "updated_at": book.updated_at.isoformat() if book.updated_at else None,
            "stats": {
                "owners_count": owners_count or 0,
                "copies_count": copies_count or 0,
                "loans_count": loans_count or 0,
                "active_loans_count": active_loans_count or 0
            },
            "owners": owners
        }
    
    async def delete_book(self, book_id: UUID, force: bool = False) -> dict:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(str(book_id))
        
        if not force:
            active_loans = await self._db.scalar(select(func.count()).select_from(Loan).join(UserBook, Loan.user_book_id == UserBook.id).where(
                    UserBook.book_id == book_id,
                    Loan.status == "active"
                )
            )
            
            if active_loans and active_loans > 0:
                raise BookHasActiveLoansException(book_id, active_loans)
        
        await self._book_repo.delete(book_id)
        
        logger.info(f"Admin deleted book {book_id}")
        return {"id": str(book_id), "deleted": True}
    
    async def merge_books(self, source_book_id: UUID, target_book_id: UUID) -> dict:
        if source_book_id == target_book_id:
            raise ValueError("Cannot merge book with itself")
        source = await self._book_repo.get_by_id(source_book_id)
        if not source:
            raise BookNotFoundException(str(source_book_id))
        target = await self._book_repo.get_by_id(target_book_id)
        if not target:
            raise BookNotFoundException(str(target_book_id))
        stmt = select(UserBook).where(UserBook.book_id == source_book_id)
        result = await self._db.execute(stmt)
        user_books = result.scalars().all()
        moved_count = 0
        for ub in user_books:
            ub.book_id = target_book_id
            moved_count += 1
        
        await self._db.commit()
        await self._book_repo.delete(source_book_id)
        
        logger.info(
            f"Admin merged book {source_book_id} into {target_book_id}. "
            f"Moved {moved_count} copies."
        )
        return {
            "source_id": str(source_book_id),
            "target_id": str(target_book_id),
            "moved_copies": moved_count
        }
    
    async def update_book_metadata(self, book_id: UUID, metadata: dict) -> dict:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(str(book_id))
        
        allowed_fields = [
            "title", "author", "description", "publisher",
            "publication_year", "page_count", "language", 
            "genre", "cover_url"
        ]
        
        update_data = {
            k: v for k, v in metadata.items()
            if k in allowed_fields
        }
        
        if not update_data:
            return {"id": str(book_id), "message": "No valid fields to update"}
        
        updated = await self._book_repo.update(book_id, update_data)
        
        logger.info(f"Admin updated metadata for book {book_id}")
        return {
            "id": str(book_id),
            "updated_fields": list(update_data.keys()),
            "book": {
                "id": str(updated.id),
                "title": updated.title,
                "author": updated.author,
                "isbn": updated.isbn
            }
        }
