from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from src.api.deps import get_user_service
from src.schemas.user import UserUpdate, UserResponse
from src.services.interfaces import IUserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user(user_id: str, user_service: IUserService = Depends(get_user_service),):
    try:
        return await user_service.get_by_id(UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{user_id}/profile", response_model=dict, summary="Get user profile")
async def get_user_profile(user_id: str, user_service: IUserService = Depends(get_user_service),):
    try:
        profile = await user_service.get_profile(UUID(user_id))
        return {
            "success": True,
            "data": {"profile": profile.model_dump()}
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{user_id}", response_model=UserResponse, summary="Update user")
async def update_user(user_id: str, user_update: UserUpdate, user_service: IUserService = Depends(get_user_service),):
    try:
        return await user_service.update(UUID(user_id), user_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
