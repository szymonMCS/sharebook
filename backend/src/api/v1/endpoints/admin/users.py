import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_active_admin, get_db
from src.services.admin import UserAdminService
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


class UpdateRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(reader|admin)$", description="New role: 'reader' or 'admin'")

def get_user_admin_service(db: AsyncSession = Depends(get_db)) -> UserAdminService:
    return UserAdminService(db)

@router.get("", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1, description="Numer strony"),
    per_page: int = Query(20, ge=1, le=100, description="Ilość na stronę"),
    search: str = Query(None, description="Wyszukiwanie (opcjonalne)"),
    current_user: User = Depends(get_current_active_admin),
    user_service: UserAdminService = Depends(get_user_admin_service)
):
    result = await user_service.list_users(page=page, per_page=per_page, search=search)
    
    return {
        "success": True,
        "data": {
            "data": result.data,
            "total": result.total,
            "page": result.page,
            "per_page": result.per_page,
            "total_pages": result.total_pages
        },
        "message": "Users retrieved"
    }

@router.get("/{user_id}", response_model=dict)
async def get_user_details(user_id: UUID, current_user: User = Depends(get_current_active_admin), user_service: UserAdminService = Depends(get_user_admin_service)):
    result = await user_service.get_user_details(user_id)
    return {
        "success": True,
        "data": result,
        "message": "User details retrieved"
    }

@router.patch("/{user_id}/role", response_model=dict)
async def update_role(
    user_id: UUID,
    role_data: UpdateRoleRequest,
    current_user: User = Depends(get_current_active_admin),
    user_service: UserAdminService = Depends(get_user_admin_service)
):
    result = await user_service.update_user_role(user_id=user_id, new_role=role_data.role, current_admin_id=current_user.id)
    return {
        "success": True,
        "data": result,
        "message": f"Rola zmieniona na: {result['role']}"
    }

@router.post("/{user_id}/reset-password", response_model=dict)
async def reset_password(user_id: UUID, current_user: User = Depends(get_current_active_admin), user_service: UserAdminService = Depends(get_user_admin_service)):
    result = await user_service.reset_user_password(user_id=user_id, current_admin_id=current_user.id)
    return {
        "success": True,
        "data": result,
        "message": "Hasło zresetowane. Użytkownik powinien je zmienić przy pierwszym logowaniu."
    }

@router.post("/{user_id}/deactivate", response_model=dict)
async def deactivate_user(user_id: UUID, current_user: User = Depends(get_current_active_admin), user_service: UserAdminService = Depends(get_user_admin_service)):
    result = await user_service.deactivate_user(user_id=user_id, current_admin_id=current_user.id)
    return {
        "success": True,
        "data": result,
        "message": "Użytkownik dezaktywowany"
    }

@router.post("/{user_id}/activate", response_model=dict)
async def activate_user(user_id: UUID, current_user: User = Depends(get_current_active_admin), user_service: UserAdminService = Depends(get_user_admin_service)):
    result = await user_service.activate_user(user_id=user_id, current_admin_id=current_user.id)
    return {
        "success": True,
        "data": result,
        "message": "Użytkownik aktywowany"
    }

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: UUID, current_user: User = Depends(get_current_active_admin), user_service: UserAdminService = Depends(get_user_admin_service)):
    await user_service.delete_user(user_id=user_id, current_admin_id=current_user.id, hard_delete=True)
    return {
        "success": True,
        "message": "Użytkownik usunięty"
    }
