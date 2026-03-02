from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Optional
from src.api.deps import get_book_catalog_service, get_current_user_optional
from src.services.interfaces import IBookCatalogService
from src.schemas.book import BookResponse
from database.models import User

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=dict)
async def search_books(
    query: Optional[str] = Query(None, description="Search in title, author, description"),
    author: Optional[str] = Query(None, description="Filter by author"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    catalog_service: IBookCatalogService = Depends(get_book_catalog_service)
):
    from src.core.response import create_pagination_meta
    
    skip = (page - 1) * per_page
    books, total = await catalog_service.search(
        query=query,
        author=author,
        genre=genre,
        skip=skip,
        limit=per_page
    )
    
    return {
        "success": True,
        "data": books,
        "meta": {
            "pagination": create_pagination_meta(page, per_page, total)
        }
    }


@router.get("/{book_id}", response_model=dict)
async def get_book(
    book_id: UUID,
    catalog_service: IBookCatalogService = Depends(get_book_catalog_service)
):
    try:
        book = await catalog_service.get_by_id(book_id)
        return {
            "success": True,
            "data": book
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/isbn/{isbn}", response_model=dict)
async def get_book_by_isbn(
    isbn: str,
    catalog_service: IBookCatalogService = Depends(get_book_catalog_service)
):
    book = await catalog_service.get_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {
        "success": True,
        "data": book
    }
