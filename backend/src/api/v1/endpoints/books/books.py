import logging
from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from typing import Optional
from src.api.deps import get_book_service, get_current_active_admin
from src.services.interfaces.books import IBookService
from src.core.response import create_pagination_meta
from src.schemas.book import BookCreate, BookUpdate, BookResponse
from src.core.exceptions import BookNotFoundException, DuplicateISBNException

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


@router.get("/{book_id}", response_model=dict)
async def get_book(book_id: UUID, book_service: IBookService = Depends(get_book_service)):
    book = await book_service.get_book(book_id)
    return {"success": True, "data": book}

@router.get("/isbn/{isbn}", response_model=dict)
async def get_book_by_isbn(isbn: str, book_service: IBookService = Depends(get_book_service)):
    book = await book_service.get_by_isbn(isbn)
    if not book:
        raise BookNotFoundException()
    return {"success": True, "data": book}

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, current_user = Depends(get_current_active_admin), book_service: IBookService = Depends(get_book_service),):
    existing = await book_service.get_by_isbn(book_data.isbn)
    if existing:
        raise DuplicateISBNException(book_data.isbn)
    book = await book_service.create_book(book_data)
    return book

@router.put("/{book_id}", response_model=BookResponse)
async def update_book(book_id: UUID, book_data: BookUpdate, current_user = Depends(get_current_active_admin), book_service: IBookService = Depends(get_book_service),):
    book = await book_service.update_book(book_id, book=book_data)
    return book

@router.patch("/{book_id}", response_model=BookResponse)
async def partial_update_book(book_id: UUID, book_data: BookUpdate, current_user = Depends(get_current_active_admin), book_service: IBookService = Depends(get_book_service),):
    update_data = book_data.model_dump(exclude_unset=True)
    if not update_data:
        from src.core.exceptions import ValidationException
        raise ValidationException("No fields to update")
    book = await book_service.update_book(book_id, book=book_data)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, current_user = Depends(get_current_active_admin),  book_service: IBookService = Depends(get_book_service),):
    await book_service.delete_book(book_id)
    return None
