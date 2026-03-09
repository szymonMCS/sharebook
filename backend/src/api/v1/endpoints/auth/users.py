from fastapi import APIRouter, Depends, status
from uuid import UUID
from src.api.deps import get_auth_service, get_current_active_user
from src.schemas.user import UserUpdate, UserResponse
from src.services.interfaces.auth import IAuthService
from src.core.exceptions import NotAuthorizedException, NotFoundException
from database.models import User

router = APIRouter(prefix="/users", tags=["users"])

def _can_access_user_resource(current_user: User, target_user_id: UUID) -> bool:
    return current_user.id == target_user_id or current_user.role == "admin"

@router.get("/me", response_model=dict, summary="Get current user")
async def get_me(current_user: User = Depends(get_current_active_user)):
    return {
        "success": True,
        "data": {
            "user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "role": current_user.role,
                "is_active": current_user.is_active,
                "location": current_user.location,
                "phone": current_user.phone,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            }
        }
    }

@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user(user_id: UUID, current_user: User = Depends(get_current_active_user), user_service: IAuthService = Depends(get_auth_service),):
    if not _can_access_user_resource(current_user, user_id):
        raise NotAuthorizedException("Access denied")
    return await user_service.get_user_by_id(user_id)

@router.get("/{user_id}/profile", response_model=dict, summary="Get user profile")
async def get_user_profile(user_id: UUID, current_user: User = Depends(get_current_active_user), user_service: IAuthService = Depends(get_auth_service),):
    if not _can_access_user_resource(current_user, user_id):
        raise NotAuthorizedException("Access denied")
    profile = await user_service.get_profile(user_id)
    return {"success": True, "data": {"profile": profile.model_dump()}}

@router.patch("/{user_id}", response_model=UserResponse, summary="Update user")
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: IAuthService = Depends(get_auth_service),
):
    if not _can_access_user_resource(current_user, user_id):
        raise NotAuthorizedException("Access denied")
    return await user_service.update_profile(user_id, user_update)
