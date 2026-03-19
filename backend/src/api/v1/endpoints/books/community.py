import logging
from typing import Optional
from fastapi import APIRouter, Depends
from src.api.deps import (
    get_book_service,
    get_current_user_optional
)
from src.services.interfaces.books import IBookService
from src.schemas.book import CommunityBooksFilter
from src.core.response import create_pagination_meta
from database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/community", tags=["community"])

@router.get("/books", response_model=dict)
async def get_community_books(
    filters: CommunityBooksFilter = Depends(),
    book_service: IBookService = Depends(get_book_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    skip = (filters.page - 1) * filters.per_page
    user_id = current_user.id if current_user else None
    
    logger.info(f"[DEBUG] Community books request - user_id: {user_id}, filters: status={filters.status}, search={filters.search}, author={filters.author}")

    books = await book_service.get_community_books(
        user_id=user_id,
        status=filters.status,
        search=filters.search,
        author=filters.author,
        skip=skip,
        limit=filters.per_page
    )
    total = await book_service.count_community_books(
        user_id=user_id,
        status=filters.status,
        search=filters.search,
        author=filters.author
    )
    
    # Log details about returned books
    for book in books:
        logger.info(f"[DEBUG] Book returned: id={book.id}, title={book.title[:30] if book.title else 'N/A'}, owner_id={book.owner_id}, status={book.status}")
    
    logger.info(f"[DEBUG] Found total={total}, returned {len(books)} books")
    
    return {
        "success": True,
        "data": books,
        "meta": {
            "pagination": create_pagination_meta(filters.page, filters.per_page, total)
        }
    }
