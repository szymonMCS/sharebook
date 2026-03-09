from uuid import UUID
from fastapi import Depends, Query
from src.api.deps import get_current_active_user, get_user_book_service
from src.services.interfaces.books import IUserBookService
from src.core.exceptions import NotFoundException
from src.api.v1.endpoints.library.routes import router
from database.models import User


@router.get("", response_model=dict)
async def get_my_library(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    library_service: IUserBookService = Depends(get_user_book_service),
    current_user: User = Depends(get_current_active_user)
):
    library = await library_service.get_user_library(user_id=current_user.id)
    total = len(library)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated = library[start_idx:end_idx]

    return {
        "success": True,
        "user_id": str(current_user.id),
        "data": paginated,
        "meta": {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            }
        }
    }

@router.get("/{user_book_id}", response_model=dict)
async def get_my_book(user_book_id: UUID, library_service: IUserBookService = Depends(get_user_book_service), current_user: User = Depends(get_current_active_user)):
    book = await library_service.get_user_book_copy(user_id=current_user.id, user_book_id=user_book_id)
    if not book:
        raise NotFoundException("Book", user_book_id)
    return {
        "success": True, 
        "data": book
    }
