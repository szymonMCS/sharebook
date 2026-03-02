import logging
from uuid import UUID
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from src.api.deps import (
    get_library_management_service,
    get_community_book_service,
    get_book_import_service,
    get_current_active_user,
    get_current_user_optional
)
from src.services.interfaces import (
    ILibraryManagementService,
    ICommunityBookService,
    IBookImportService
)
from src.schemas.book import (
    AddBookToLibraryRequest,
    UserBookResponse,
    UpdateLendableRequest,
    UpdateStatusRequest,
    CommunityBooksFilter
)
from src.core.exceptions import ShareBookException
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/library", tags=["library"])


@router.get("/my-books", response_model=dict)
async def get_my_library(
    skip: int = 0,
    limit: int = 100,
    library_service: ILibraryManagementService = Depends(get_library_management_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        library = await library_service.get_library(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        return {
            "success": True,
            "user_id": str(current_user.id),
            "total_books": len(library),
            "books": library
        }
    except Exception as e:
        logger.exception("Error fetching library")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my-books/{user_book_id}", response_model=dict)
async def get_my_book(
    user_book_id: UUID,
    library_service: ILibraryManagementService = Depends(get_library_management_service),
    current_user: User = Depends(get_current_active_user)
):
    book = await library_service.get_library_item(
        user_id=current_user.id,
        user_book_id=user_book_id
    )
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in your library"
        )
    
    return {
        "success": True,
        "data": book
    }


@router.post("/books", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_book_to_library(
    request: AddBookToLibraryRequest,
    background_tasks: BackgroundTasks,
    library_service: ILibraryManagementService = Depends(get_library_management_service),
    import_service: IBookImportService = Depends(get_book_import_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        result = await library_service.add_book_to_library(
            user_id=current_user.id,
            isbn=request.isbn,
            condition=request.condition
        )
        
        if result.book.title == "Wczytywanie...":
            background_tasks.add_task(
                import_service.enrich_book_data,
                result.book.id
            )
        
        return {
            "success": True,
            "message": "Book added to library. Data will be enriched shortly." if result.book.title == "Wczytywanie..." else "Book added to library.",
            "data": result
        }
        
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error adding book to library")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/my-books/{user_book_id}/lendable", response_model=dict)
async def update_lendable_status(
    user_book_id: UUID,
    update_data: UpdateLendableRequest,
    library_service: ILibraryManagementService = Depends(get_library_management_service),
    current_user: User = Depends(get_current_active_user)
):
    
    try:
        result = await library_service.update_lendable_status(
            user_id=current_user.id,
            user_book_id=user_book_id,
            is_lendable=update_data.is_lendable
        )
        
        return {
            "success": True,
            "message": f"Lending status updated to: {'yes' if result.is_lendable else 'no'}",
            "data": result
        }
        
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error updating lendable status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/my-books/{user_book_id}/status", response_model=dict)
async def update_book_status(
    user_book_id: UUID,
    status_update: UpdateStatusRequest,
    library_service: ILibraryManagementService = Depends(get_library_management_service),
    current_user: User = Depends(get_current_active_user)
):
    
    try:
        result = await library_service.update_status(
            user_id=current_user.id,
            user_book_id=user_book_id,
            status=status_update.status
        )
        
        return {
            "success": True,
            "message": f"Status updated to: {status_update.status}",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error updating book status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/my-books/{user_book_id}", response_model=dict)
async def remove_from_library(
    user_book_id: UUID,
    library_service: ILibraryManagementService = Depends(get_library_management_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        success = await library_service.remove_from_library(
            user_id=current_user.id,
            user_book_id=user_book_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Book removed from library"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
            
    except ValueError as e:
        error_msg = str(e)
        if "borrowed" in error_msg.lower() or "lent" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove borrowed or lent book. Wait for return first."
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error removing book from library")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/community", response_model=dict)
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
