import uuid
import logging
from uuid import UUID
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import IBookRepository, IUserBookRepository, IUserRepository
from src.schemas.book import BookCreate
from src.services.book_discovery import UnifiedBookSearch

logger = logging.getLogger(__name__)


class UserBookService:
    def __init__(
        self,
        db: AsyncSession,
        user_book_repo: Optional[IUserBookRepository] = None,
        book_repo: Optional[IBookRepository] = None,
        user_repo: Optional[IUserRepository] = None
    ):
        self.db = db
        self.user_book_repo = user_book_repo
        self.book_repo = book_repo
        self.user_repo = user_repo
    
    async def _fetch_book_data_from_ai(self, isbn: str) -> Optional[Dict[str, Any]]:
        try:
            search = UnifiedBookSearch()
            result = await search.search_by_isbn(isbn)
            
            if result.success and result.data:
                data = result.data
                return {
                    "title": data.get("full_title", "Unknown Title"),
                    "author": data.get("author", "Unknown Author"),
                    "description": data.get("short_description"),
                    "cover_url": data.get("cover_image_url"),
                    "page_count": data.get("page_count"),
                    "publication_year": data.get("publication_year"),
                    "genre": data.get("genre"),
                    "language": data.get("language", "pl"),
                }
            else:
                logger.warning(f"AI search returned no results for ISBN: {isbn}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to fetch book data from AI for ISBN {isbn}: {e}")
            return None
    
    async def add_book_to_user(
        self,
        user_id: UUID,
        book_data: BookCreate,
        condition: Optional[str] = None,
        is_lendable: bool = True,
        user_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        existing_book = await self.book_repo.get_by_isbn(book_data.isbn)
        
        if not existing_book:
            title = book_data.title
            author = book_data.author
            description = book_data.description
            page_count = book_data.page_count
            publication_year = book_data.publication_year
            genre = book_data.genre
            language = book_data.language
            
            if not title or not author:
                logger.info(f"Fetching book data from AI for ISBN: {book_data.isbn}")
                ai_data = await self._fetch_book_data_from_ai(book_data.isbn)
                if ai_data:
                    title = title or ai_data.get("title", "Brak tytułu")
                    author = author or ai_data.get("author", "Nieznany autor")
                    description = description or ai_data.get("description")
                    page_count = page_count or ai_data.get("page_count")
                    publication_year = publication_year or ai_data.get("publication_year")
                    genre = genre or ai_data.get("genre")
                    language = language or ai_data.get("language", "pl")
                else:
                    title = title or "Książka bez tytułu"
                    author = author or "Nieznany autor"
            
            book = await self.book_repo.create({
                "isbn": book_data.isbn,
                "title": title,
                "author": author,
                "description": description,
                "publisher": book_data.publisher,
                "publication_year": publication_year,
                "page_count": page_count,
                "language": language or "pl",
                "genre": genre
            })
            is_new_book = True
        else:
            book = existing_book
            is_new_book = False
        
        user_book = await self.user_book_repo.create({
            "user_id": user_id,
            "book_id": book.id,
            "status": "available",
            "condition": condition,
            "is_lendable": is_lendable,
        })
        
        return {
            "status": "added",
            "is_new_book": is_new_book,
            "book": book,
            "user_book": user_book
        }
    
    async def add_book_with_placeholder(self, user_id: UUID, isbn: str, condition: Optional[str] = None, is_lendable: bool = True) -> Dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        existing_book = await self.book_repo.get_by_isbn(isbn)
        
        if not existing_book:
            book = await self.book_repo.create({
                "isbn": isbn,
                "title": "Wczytywanie...",
                "author": "",
                "description": "",
                "publisher": None,
                "publication_year": None,
                "page_count": None,
                "language": "pl",
                "genre": None
            })
            is_new_book = True
        else:
            book = existing_book
            is_new_book = False
  
        user_book = await self.user_book_repo.create({
            "user_id": user_id,
            "book_id": book.id,
            "status": "available",
            "condition": condition,
            "is_lendable": is_lendable,
        })
        
        return {
            "id": str(user_book.id),
            "book_id": str(book.id),
            "status": "added",
            "is_new_book": is_new_book
        }
    
    async def get_user_library(self, user_id: UUID) -> List[Dict[str, Any]]:
        results = await self.user_book_repo.get_user_library(user_id)
        
        library_items = []
        for user_book, book in results:
            library_items.append({
                "id": str(user_book.id),
                "book_id": str(book.id),
                "book": {
                    "id": str(book.id),
                    "isbn": book.isbn,
                    "title": book.title,
                    "author": book.author,
                    "cover_url": f"/covers/{book.isbn}.jpg" if book.isbn else None,
                    "description": book.description,
                    "genre": book.genre,
                    "publication_year": book.publication_year,
                },
                "status": user_book.status,
                "condition": user_book.condition,
                "is_lendable": user_book.is_lendable,
                "user_notes": user_book.user_notes if hasattr(user_book, 'user_notes') else None,
                "added_at": user_book.added_at.isoformat() if user_book.added_at else None,
            })
        
        return library_items
    
    async def remove_from_library(self, user_id: UUID, user_book_id: UUID) -> bool:
        user_book = await self.user_book_repo.get_by_id(user_book_id)
        if not user_book:
            return False
        if user_book.user_id != user_id:
            raise PermissionError("Not authorized to remove this book")
        return await self.user_book_repo.delete(user_book_id)
    
    async def remove_book_from_user(self, user_id: UUID, user_book_id: UUID) -> bool:
        return await self.remove_from_library(user_id, user_book_id)
    
    async def toggle_lendable(self, user_id: UUID, user_book_id: UUID) -> Optional[Dict[str, Any]]:
        user_book = await self.user_book_repo.get_by_id(user_book_id)
        if not user_book:
            return None
        if user_book.user_id != user_id:
            raise PermissionError("Not authorized to modify this book")
        new_value = not user_book.is_lendable
        updated = await self.user_book_repo.update(user_book_id, is_lendable=new_value)
        if updated:
            return {
                "id": str(updated.id),
                "is_lendable": updated.is_lendable,
                "status": updated.status
            }
        return None
    
    toggle_lendable_by_id = toggle_lendable
    
    async def set_lendable_by_id(self, user_id: UUID, user_book_id: UUID, is_lendable: bool) -> Optional[Dict[str, Any]]:
        user_book = await self.user_book_repo.get_by_id(user_book_id)
        if not user_book:
            return None
        if user_book.user_id != user_id:
            raise PermissionError("Not authorized to modify this book")
        if user_book.is_lendable != is_lendable:
            updated = await self.user_book_repo.update(user_book_id, is_lendable=is_lendable)
        else:
            updated = user_book
        return {
            "id": str(updated.id),
            "is_lendable": updated.is_lendable,
            "status": updated.status
        }
    
    async def get_by_isbn_and_user(self, isbn: str, user_id: UUID) -> Optional[Dict[str, Any]]:
        book = await self.book_repo.get_by_isbn(isbn)
        if not book:
            return None
        user_book = await self.user_book_repo.get_by_user_and_book(user_id, book.id)
        if user_book:
            return {
                "id": str(user_book.id),
                "book_id": str(book.id),
                "isbn": book.isbn,
                "status": user_book.status,
            }
        return None
    
    async def update_status(self, user_id: UUID, book_id: UUID, new_status: str) -> Optional[Dict[str, Any]]:
        user_book = await self.user_book_repo.get_by_user_and_book(user_id, book_id)
        if not user_book:
            return None
        if user_book.user_id != user_id:
            raise PermissionError("Not authorized to modify this book")
        
        valid_statuses = ['available', 'reserved', 'borrowed', 'unavailable', 'lent']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        updated = await self.user_book_repo.update(user_book.id, status=new_status)
        
        return {
            "id": str(updated.id),
            "status": updated.status
        }
    
    async def update_book_status(self, user_id: UUID, user_book_id: UUID, new_status: str) -> Optional[Dict[str, Any]]:
        user_book = await self.user_book_repo.get_by_id(user_book_id)
        if not user_book:
            return None
        if user_book.user_id != user_id:
            raise PermissionError("Not authorized to modify this book")
        valid_statuses = ['available', 'reserved', 'borrowed', 'unavailable', 'lent']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        updated = await self.user_book_repo.update(user_book_id, {"status": new_status})
        
        return {
            "id": str(updated.id),
            "status": updated.status
        }
    
    async def get_user_book_copy(self, user_id: UUID, user_book_id: UUID) -> Optional[Dict[str, Any]]:
        user_book = await self.user_book_repo.get_by_id(user_book_id)
        if not user_book or user_book.user_id != user_id:
            return None
        book = await self.book_repo.get_by_id(user_book.book_id)
        if not book:
            return None
        owner_user = await self.user_repo.get_by_id(user_id)
        
        return {
            "id": str(user_book.id),
            "book_id": str(book.id),
            "isbn": book.isbn,
            "title": book.title or "Brak tytułu",
            "author": book.author or "Nieznany autor",
            "description": book.description,
            "cover_url": f"/covers/{book.isbn}.jpg" if book.isbn else None,
            "publisher": book.publisher,
            "publication_year": book.publication_year,
            "page_count": book.page_count,
            "language": book.language or "pl",
            "genre": book.genre,
            "status": user_book.status,
            "condition": user_book.condition,
            "is_lendable": user_book.is_lendable,
            "owner_id": str(user_id),
            "owner": {
                "id": str(user_id),
                "first_name": owner_user.first_name if owner_user else "",
                "last_name": owner_user.last_name if owner_user else "",
                "location": owner_user.location if owner_user else None
            },
            "created_at": book.created_at.isoformat() if book.created_at else None,
        }
    
    async def remove_from_library_by_id(self, user_id: UUID, user_book_id: UUID) -> Dict[str, Any]:
        user_book = await self.user_book_repo.get_by_id(user_book_id)
        if not user_book or user_book.user_id != user_id:
            raise ValueError("Book not found or access denied")
        if user_book.status in ['borrowed', 'lent']:
            raise ValueError("Cannot remove borrowed book")
        
        success = await self.user_book_repo.delete(user_book_id)
        
        if not success:
            raise ValueError("Failed to remove book")
        
        return {"success": True, "message": "Book removed from library"}
    
    async def get_book_for_discovery(self, user_id: UUID, book_id: UUID) -> Dict[str, Any]:
        user_book = await self.user_book_repo.get_by_user_and_book(user_id, book_id)
        
        if not user_book:
            raise ValueError("Book not found or access denied")
        
        book = await self.book_repo.get_by_id(book_id)
        
        if not book or not book.isbn:
            raise ValueError("Book has no ISBN")
        
        return {
            "book_id": str(book_id),
            "isbn": book.isbn,
            "title": book.title or "Wczytywanie...",
            "author": book.author or "",
            "genre": book.genre or "",
            "description": book.description or ""
        }
