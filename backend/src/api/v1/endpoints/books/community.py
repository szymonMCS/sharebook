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

router = APIRouter(prefix="/community", tags=["community"])

@router.get("/books", response_model=dict)
async def get_community_books(
    filters: CommunityBooksFilter = Depends(),
    book_service: IBookService = Depends(get_book_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    skip = (filters.page - 1) * filters.per_page

    books = await book_service.get_community_books(
        user_id=current_user.id if current_user else None,
        status=filters.status,
        search=filters.search,
        author=filters.author,
        skip=skip,
        limit=filters.per_page
    )
    total = await book_service.count_community_books(
        user_id=current_user.id if current_user else None,
        status=filters.status,
        search=filters.search,
        author=filters.author
    )
    return {
        "success": True,
        "data": books,
        "meta": {
            "pagination": create_pagination_meta(filters.page, filters.per_page, total)
        }
    }
