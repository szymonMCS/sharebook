import logging
from fastapi import APIRouter, Depends, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from src.api.deps import get_book_service, get_current_active_admin, get_current_active_user, get_db
from src.services.interfaces.books import IBookService
from src.core.response import create_pagination_meta
from src.schemas.book import BookCreate, BookUpdate, BookResponse
from src.core.exceptions import BookNotFoundException, DuplicateISBNException
from src.api.v1.endpoints.background_tasks import enrich_and_fetch_cover_background
from database.repositories.book_repository import BookRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/books", tags=["books"])

@router.get("", response_model=dict)
async def search_books(
    query: Optional[str] = Query(None, description="Search in title, author, description"),
    author: Optional[str] = Query(None, description="Filter by author"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    book_service: IBookService = Depends(get_book_service)
):
    skip = (page - 1) * per_page
    books, total = await book_service.search(query=query, author=author, genre=genre, skip=skip, limit=per_page)
    return {
        "success": True,
        "data": books,
        "meta": {
            "pagination": create_pagination_meta(page, per_page, total)
        }
    }

@router.post("/{book_id}/enrich", response_model=dict)
async def enrich_book(
    book_id: UUID,
    background_tasks: BackgroundTasks,
    book_service: IBookService = Depends(get_book_service),
    db: AsyncSession = Depends(get_db)
):
    book = await book_service.get_book(book_id)
    if not book:
        raise BookNotFoundException()
    
    book_repo = BookRepository(db)
    book_db = await book_repo.get_by_id(book_id)
    if book_db is None:
        raise BookNotFoundException()
    if book_db.title in ["", "Wczytywanie...", "Unknown"] or not book_db.author:
        background_tasks.add_task(
            enrich_and_fetch_cover_background,
            book_id=book_id,
            isbn=book_db.isbn,
            db=db
        )
        return {"success": True, "message": "Enrichment started", "status": "processing"}
    else:
        return {"success": True, "message": "Book already enriched", "status": "completed"}

@router.get("/{book_id}", response_model=dict)
async def get_book(book_id: UUID, book_service: IBookService = Depends(get_book_service)):
    book = await book_service.get_book(book_id)
    return {"success": True, "data": book}

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, current_user = Depends(get_current_active_user), book_service: IBookService = Depends(get_book_service),):
    existing = await book_service.get_by_isbn(book_data.isbn)
    if existing:
        raise DuplicateISBNException(book_data.isbn)
    book = await book_service.create_book(book_data)
    return book

@router.put("/{book_id}", response_model=BookResponse)
async def update_book(book_id: UUID, book_data: BookUpdate, current_user = Depends(get_current_active_admin), book_service: IBookService = Depends(get_book_service),):
    book = await book_service.update_book(book_id, user_id=current_user.id, data=book_data)
    return book

@router.patch("/{book_id}", response_model=BookResponse)
async def partial_update_book(book_id: UUID, book_data: BookUpdate, current_user = Depends(get_current_active_admin), book_service: IBookService = Depends(get_book_service),):
    update_data = book_data.model_dump(exclude_unset=True)
    if not update_data:
        from src.core.exceptions import ValidationException
        raise ValidationException("No fields to update")
    book = await book_service.update_book(book_id, user_id=current_user.id, data=book_data)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, current_user = Depends(get_current_active_admin),  book_service: IBookService = Depends(get_book_service),):
    await book_service.delete_book(book_id, user_id=current_user.id)
    return None
