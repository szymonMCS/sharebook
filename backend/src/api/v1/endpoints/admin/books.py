import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_active_admin, get_db
from src.services.admin import BookAdminService
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


class BookMetadataUpdate(BaseModel):
    title: str | None = Field(None, description="Book title")
    author: str | None = Field(None, description="Book author")
    description: str | None = Field(None, description="Book description")
    publisher: str | None = Field(None, description="Publisher")
    publication_year: int | None = Field(None, description="Publication year")
    page_count: int | None = Field(None, description="Number of pages")
    language: str | None = Field(None, description="Language code")
    genre: str | None = Field(None, description="Genre")
    cover_url: str | None = Field(None, description="Cover image URL")

def get_book_admin_service(db: AsyncSession = Depends(get_db)) -> BookAdminService:
    return BookAdminService(db)

@router.get("", response_model=dict)
async def get_books(
    page: int = Query(1, ge=1, description="Numer strony"),
    per_page: int = Query(20, ge=1, le=100, description="Ilość na stronę"),
    search: str = Query(None, description="Wyszukiwanie (tytuł, autor, ISBN)"),
    current_user: User = Depends(get_current_active_admin),
    book_service: BookAdminService = Depends(get_book_admin_service)
):
    result = await book_service.list_books(page=page, per_page=per_page, search=search)
    return {
        "success": True,
        "data": {
            "data": result.data,
            "total": result.total,
            "page": result.page,
            "per_page": result.per_page,
            "total_pages": result.total_pages
        },
        "message": "Books retrieved"
    }

@router.get("/{book_id}", response_model=dict)
async def get_book_details(book_id: UUID, current_user: User = Depends(get_current_active_admin), book_service: BookAdminService = Depends(get_book_admin_service)):
    result = await book_service.get_book_details(book_id)
    return {
        "success": True,
        "data": result,
        "message": "Book details retrieved"
    }

@router.patch("/{book_id}", response_model=dict)
async def update_book_metadata(
    book_id: UUID,
    metadata: BookMetadataUpdate,
    current_user: User = Depends(get_current_active_admin),
    book_service: BookAdminService = Depends(get_book_admin_service)
):
    result = await book_service.update_book_metadata(book_id=book_id, metadata=metadata.model_dump(exclude_unset=True))
    return {
        "success": True,
        "data": result,
        "message": "Book metadata updated"
    }

@router.post("/merge", response_model=dict)
async def merge_books(
    source_id: UUID,
    target_id: UUID,
    current_user: User = Depends(get_current_active_admin),
    book_service: BookAdminService = Depends(get_book_admin_service)
):
    result = await book_service.merge_books(source_book_id=source_id, target_book_id=target_id)
    return {
        "success": True,
        "data": result,
        "message": f"Books merged. Moved {result['moved_copies']} copies."
    }

@router.delete("/{book_id}", response_model=dict)
async def delete_book(
    book_id: UUID,
    force: bool = Query(False, description="Force delete even with active loans"),
    current_user: User = Depends(get_current_active_admin),
    book_service: BookAdminService = Depends(get_book_admin_service)
):
    await book_service.delete_book(book_id, force=force)
    return {
        "success": True,
        "message": "Książka usunięta"
    }
