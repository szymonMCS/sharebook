from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.api.deps import get_db
from src.schemas.user import UserCreate, UserResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def _handle_service_error(exc: ValueError, status_code: int = status.HTTP_400_BAD_REQUEST):
    raise HTTPException(status_code=status_code, detail=str(exc))


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Zarejestruj nowego użytkownika",
)
async def register(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.register(user_data)
    except ValueError as e:
        _handle_service_error(e, status.HTTP_400_BAD_REQUEST)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Pobierz dane użytkownika",
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.get_by_id(UUID(user_id))
    except ValueError as e:
        _handle_service_error(e, status.HTTP_404_NOT_FOUND)
