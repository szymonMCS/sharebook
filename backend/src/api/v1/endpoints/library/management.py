from uuid import UUID
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_active_user, verify_csrf_protection, get_db, get_user_book_service
from src.services.interfaces.books import IUserBookService
from src.schemas.book import AddBookToLibraryRequest, UpdateLendableRequest, UpdateStatusRequest
from src.core.exceptions import NotFoundException, NotAuthorizedException, InvalidBookStatusException
from src.api.v1.endpoints.background_tasks import enrich_and_fetch_cover_background
from src.api.v1.endpoints.library.routes import router
from database.models import User

management_router = APIRouter()

@management_router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_book_to_library(
    request: AddBookToLibraryRequest,
    background_tasks: BackgroundTasks,
    library_service: IUserBookService = Depends(get_user_book_service),
    current_user: User = Depends(verify_csrf_protection),
    db: AsyncSession = Depends(get_db)
):
    result = await library_service.add_book_with_placeholder(user_id=current_user.id, isbn=request.isbn, condition=request.condition)
    background_tasks.add_task(
        enrich_and_fetch_cover_background,
        book_id=UUID(result["book_id"]),
        isbn=request.isbn,
        db=db
    )
    return {
        "success": True,
        "message": "Book added to library. Data and cover will be fetched shortly.",
        "data": {**result, "status": "processing"}
    }

@router.patch("/{user_book_id}/lendable", response_model=dict)
async def update_lendable_status(
    user_book_id: UUID,
    update_data: UpdateLendableRequest,
    library_service: IUserBookService = Depends(get_user_book_service),
    current_user: User = Depends(get_current_active_user)
):
    result = await library_service.set_lendable_by_id(
        user_id=current_user.id,
        user_book_id=user_book_id,
        is_lendable=update_data.is_lendable
    )
    if not result:
        raise NotFoundException("Book", user_book_id)
    return {
        "success": True,
        "message": f"Lending status updated to: {'yes' if result['is_lendable'] else 'no'}",
        "data": result
    }

@router.patch("/{user_book_id}/status", response_model=dict)
async def update_book_status(
    user_book_id: UUID,
    status_update: UpdateStatusRequest,
    library_service: IUserBookService = Depends(get_user_book_service),
    current_user: User = Depends(get_current_active_user)
):
    result = await library_service.update_book_status(
        user_id=current_user.id,
        user_book_id=user_book_id,
        new_status=status_update.status
    )
    if not result:
        raise NotFoundException("Book", user_book_id)
    return {
        "success": True,
        "message": f"Status updated to: {status_update.status}",
        "data": result
    }

@router.delete("/{user_book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_library(
    user_book_id: UUID,
    library_service: IUserBookService = Depends(get_user_book_service),
    current_user: User = Depends(get_current_active_user)
):
    success = await library_service.remove_from_library(user_id=current_user.id, user_book_id=user_book_id)
    if not success:
        raise NotFoundException("Book", user_book_id)
    return None
