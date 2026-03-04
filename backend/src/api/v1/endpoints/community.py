from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.api.deps import (
    get_community_book_service,
    get_current_user_optional
)
from src.services.interfaces import ICommunityBookService
from src.schemas.book import CommunityBooksFilter
from database.models import User

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/books", response_model=dict)
async def get_community_books(
    filters: CommunityBooksFilter = Depends(),
    community_service: ICommunityBookService = Depends(get_community_book_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    skip = (filters.page - 1) * filters.per_page

    books, total = await community_service.get_community_books(
        exclude_user_id=current_user.id if current_user else None,
        status=filters.status,
        search=filters.search,
        author=filters.author,
        skip=skip,
        limit=filters.per_page
    )
    
    from src.core.response import create_pagination_meta
    
    return {
        "success": True,
        "data": books,
        "meta": {
            "pagination": create_pagination_meta(filters.page, filters.per_page, total)
        }
    }
