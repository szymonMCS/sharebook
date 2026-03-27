import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import IBookRepository, IUserBookRepository, ILoanRepository
from database.models import UserBook, Book, User
from src.core.exceptions import BookNotFoundException
from src.services.interfaces import IBookAdminService, BookListResult

logger = logging.getLogger(__name__)


class BookHasActiveLoansException(Exception):
    def __init__(self, book_id: UUID, active_loans: int):
        self.book_id = book_id
        self.active_loans = active_loans
        super().__init__(f"Book {book_id} has {active_loans} active loans")


class BookAdminService(IBookAdminService):
    def __init__(
        self, 
        db: AsyncSession, 
        book_repo: Optional[IBookRepository] = None,
        user_book_repo: Optional[IUserBookRepository] = None,
        loan_repo: Optional[ILoanRepository] = None
    ):
        self._db = db
        self._book_repo = book_repo
        self._user_book_repo = user_book_repo
        self._loan_repo = loan_repo
        
        if self._book_repo is None:
            from database.repositories.book_repository import BookRepository
            self._book_repo = BookRepository(db)
        if self._user_book_repo is None:
            from database.repositories.user_book_repository import UserBookRepository
            self._user_book_repo = UserBookRepository(db)
        if self._loan_repo is None:
            from database.repositories.loan_repository import LoanRepository
            self._loan_repo = LoanRepository(db)
    
    async def list_books(
        self, 
        page: int = 1, 
        per_page: int = 20, 
        search: Optional[str] = None, 
        has_loans: Optional[bool] = None
    ) -> BookListResult:
        skip = (page - 1) * per_page
        
        books, total = await self._book_repo.get_multi_with_search(
            skip=skip,
            limit=per_page,
            search=search
        )
        
        data = []
        for book in books:
            stats = await self._book_repo.get_book_stats(book.id)
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
                    "owners_count": stats["owners_count"],
                    "loans_count": stats["total_loans"],
                    "active_loans": stats["active_loans"]
                }
            })
        return BookListResult(
            data=data,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page if per_page > 0 else 0
        )
    
    async def get_book_details(self, book_id: UUID) -> dict:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(str(book_id))
        
        stats = await self._book_repo.get_book_stats(book_id)
        user_books = await self._user_book_repo.get_owners_for_book(book_id)
        
        owners = []
        for ub in user_books:
            if ub.user:
                owners.append({
                    "user_book_id": str(ub.id),
                    "user_id": str(ub.user.id),
                    "email": ub.user.email,
                    "first_name": ub.user.first_name,
                    "last_name": ub.user.last_name,
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
            "stats": stats,
            "owners": owners
        }
    
    async def delete_book(self, book_id: UUID, force: bool = False) -> dict:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(str(book_id))
        
        if not force:
            stats = await self._book_repo.get_book_stats(book_id)
            active_loans = stats["active_loans"]
            
            if active_loans > 0:
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
        
        user_books = await self._user_book_repo.get_owners_for_book(source_book_id)
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
            "isbn", "title", "author", "description", "publisher",
            "publication_year", "page_count", "language", 
            "genre", "cover_url"
        ]
        
        update_data = {
            k: v for k, v in metadata.items()
            if k in allowed_fields and v is not None
        }
        
        if not update_data:
            return {"id": str(book_id), "message": "No valid fields to update"}
        
        updated = await self._book_repo.update(book_id, update_data)
        
        logger.info(f"Admin updated metadata for book {book_id}: {list(update_data.keys())}")
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
    
    async def create_book(self, book_data: dict) -> dict:
        """Create a new book in the catalog."""
        from database.models import Book
        
        book = Book(
            isbn=book_data.get("isbn", ""),
            title=book_data.get("title", "Brak tytułu"),
            author=book_data.get("author", "Nieznany autor"),
            description=book_data.get("description"),
            publisher=book_data.get("publisher"),
            publication_year=book_data.get("publication_year"),
            page_count=book_data.get("page_count"),
            language=book_data.get("language", "pl"),
            genre=book_data.get("genre")
        )
        self._db.add(book)
        await self._db.commit()
        await self._db.refresh(book)
        
        logger.info(f"Admin created book {book.id} - {book.title}")
        return {
            "id": str(book.id),
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "created_at": book.created_at.isoformat() if book.created_at else None
        }
    
    # ========== USER BOOKS MANAGEMENT ==========
    
    async def list_user_books(
        self,
        user_id: Optional[UUID] = None,
        book_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20
    ) -> BookListResult:
        """List user books with details."""
        skip = (page - 1) * per_page
        
        query = select(UserBook, Book, User).join(Book, UserBook.book_id == Book.id).join(User, UserBook.user_id == User.id)
        
        if user_id:
            query = query.where(UserBook.user_id == user_id)
        if book_id:
            query = query.where(UserBook.book_id == book_id)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.order_by(UserBook.added_at.desc()).offset(skip).limit(per_page)
        result = await self._db.execute(query)
        items = result.all()
        
        data = []
        for user_book, book, user in items:
            has_active_loan = await self._user_book_repo.has_active_loan(user_book.id)
            data.append({
                "user_book_id": str(user_book.id),
                "user_id": str(user.id),
                "user_email": user.email,
                "user_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
                "book_id": str(book.id),
                "book_title": book.title,
                "book_author": book.author,
                "book_isbn": book.isbn,
                "book_cover_url": book.cover_url,
                "status": user_book.status,
                "condition": user_book.condition,
                "is_lendable": user_book.is_lendable,
                "has_active_loan": has_active_loan,
                "added_at": user_book.added_at.isoformat() if user_book.added_at else None
            })
        
        return BookListResult(
            data=data,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page if per_page > 0 else 0
        )
    
    async def add_book_to_user(self, user_id: UUID, book_id: UUID, condition: str = "good", is_lendable: bool = True) -> dict:
        """Add a book copy to a user's library."""
        from database.models import UserBook, User
        
        # Check if user exists
        user_result = await self._db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check if book exists
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(str(book_id))
        
        # Check if user already has this book
        existing = await self._user_book_repo.get_by_book_and_user(book_id, user_id)
        if existing:
            raise ValueError(f"User already has this book (user_book_id: {existing.id})")
        
        # Create user book
        user_book = UserBook(
            user_id=user_id,
            book_id=book_id,
            status="available",
            condition=condition,
            is_lendable=is_lendable
        )
        self._db.add(user_book)
        await self._db.commit()
        await self._db.refresh(user_book)
        
        logger.info(f"Admin added book {book_id} to user {user_id} (user_book_id: {user_book.id})")
        return {
            "user_book_id": str(user_book.id),
            "user_id": str(user_id),
            "book_id": str(book_id),
            "book_title": book.title,
            "status": user_book.status,
            "message": "Książka dodana do biblioteki użytkownika"
        }
    
    async def remove_book_from_user(self, user_book_id: UUID, force: bool = False) -> dict:
        """Remove a book copy from a user's library."""
        user_book = await self._user_book_repo.get_by_id_with_relations(user_book_id)
        if not user_book:
            raise ValueError(f"User book {user_book_id} not found")
        
        # Check for active loans
        if not force:
            has_active_loan = await self._user_book_repo.has_active_loan(user_book_id)
            if has_active_loan:
                raise ValueError(f"Cannot remove book with active loan. Use force=true to override.")
        
        user_id = user_book.user_id
        book_title = user_book.book.title if user_book.book else "Unknown"
        
        await self._user_book_repo.delete(user_book_id)
        
        logger.info(f"Admin removed book {user_book_id} from user {user_id}")
        return {
            "user_book_id": str(user_book_id),
            "user_id": str(user_id),
            "book_title": book_title,
            "message": "Książka usunięta z biblioteki użytkownika"
        }
    
    async def update_user_book_status(self, user_book_id: UUID, status: str, is_lendable: Optional[bool] = None) -> dict:
        """Update user book status and lendable flag."""
        user_book = await self._user_book_repo.get_by_id_with_relations(user_book_id)
        if not user_book:
            raise ValueError(f"User book {user_book_id} not found")
        
        valid_statuses = ["available", "reserved", "borrowed", "unavailable"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        user_book.status = status
        if is_lendable is not None:
            user_book.is_lendable = is_lendable
        
        await self._db.commit()
        await self._db.refresh(user_book)
        
        logger.info(f"Admin updated user_book {user_book_id} status to {status}")
        return {
            "user_book_id": str(user_book_id),
            "status": user_book.status,
            "is_lendable": user_book.is_lendable,
            "message": "Status książki zaktualizowany"
        }
