import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
from src.core.exceptions import ValidationException
from src.services.cover import SimpleCoverResult, get_cover_service as get_cover_service_impl

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/covers", tags=["covers"])


class BookCoverRequest(BaseModel):
    isbn: str
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None


class CoverResponse(BaseModel):
    isbn: str
    status: str
    local_url: Optional[str] = None
    fallback_url: Optional[str] = None
    source: str
    ai_generated: bool = False
    error: Optional[str] = None


class BatchRequest(BaseModel):
    books: List[BookCoverRequest]
    skip_existing: bool = True


@router.post("/fetch", response_model=CoverResponse)
async def fetch_or_generate_cover(
    request: BookCoverRequest,
    background_tasks: BackgroundTasks = None,
    sync: bool = True,
    service=Depends(get_cover_service_impl),
):
    if not sync and background_tasks:
        background_tasks.add_task(
            service.fetch_cover,
            isbn=request.isbn,
            book_title=request.title,
            book_author=request.author,
            book_genre=request.genre
        )
        return CoverResponse(
            isbn=request.isbn,
            status="processing",
            fallback_url=f"https://covers.openlibrary.org/b/isbn/{request.isbn}-M.jpg",
            source="none"
        )
    result = await service.fetch_cover(
        isbn=request.isbn,
        book_title=request.title,
        book_author=request.author,
        book_genre=request.genre
    )
    return _convert_result(result)


@router.post("/batch", response_model=List[CoverResponse])
async def batch_covers(request: BatchRequest, background_tasks: BackgroundTasks = None, service=Depends(get_cover_service_impl),):
    if len(request.books) > 50:
        raise ValidationException("Max 50 books per request")
    books_data = [{"isbn": b.isbn, "title": b.title or "Unknown", "author": b.author or "Unknown", "genre": b.genre} for b in request.books]
    results = await service.batch_fetch(books_data, request.skip_existing)
    return [_convert_result(r) for r in results]

@router.get("/{isbn}.jpg")
async def get_cover_file(isbn: str, service=Depends(get_cover_service_impl)):
    if service.exists_locally(isbn):
        cover_path = service.storage.get_cover_path(isbn) if hasattr(service, 'storage') else None
        if cover_path and Path(cover_path).exists():
            return FileResponse(cover_path, media_type="image/jpeg")

    result = await service.fetch_cover(isbn)
    if result.success and result.local_path and Path(result.local_path).exists():
        return FileResponse(result.local_path, media_type="image/jpeg")
    raise HTTPException(status_code=307, headers={"Location": f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"})

def _convert_result(result: SimpleCoverResult) -> CoverResponse:
    status_map = {
        True: "cached" if result.from_cache else ("ai_generated" if result.ai_generated else "success"),
        False: "not_found" if "not found" in (result.error or "").lower() else "error"
    }

    return CoverResponse(
        isbn=result.isbn,
        status=status_map[result.success],
        local_url=result.local_url,
        fallback_url=result.openlibrary_url if not result.success else None,
        source=result.source,
        ai_generated=result.ai_generated,
        error=result.error
    )
