import logging
import secrets
from typing import Optional
from uuid import UUID
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, UserBook, Loan
from database.interfaces import IUserRepository
from src.core.security import get_password_hash
from src.core.exceptions import (
    UserNotFoundException,
    SelfModificationException,
    InvalidRoleException
)
from src.services.admin.interfaces import IUserAdminService, UserListResult

logger = logging.getLogger(__name__)


class UserAdminService(IUserAdminService):
    def __init__(self, db: AsyncSession, user_repo: Optional[IUserRepository] = None):
        self._db = db
        self._user_repo = user_repo
        
        if self._user_repo is None:
            from database.repositories.user_repository import UserRepository
            self._user_repo = UserRepository(db)
    
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserListResult:
        skip = (page - 1) * per_page
        
        query = select(User)

        if search:
            search_filter = or_(User.email.ilike(f"%{search}%"), User.first_name.ilike(f"%{search}%"), User.last_name.ilike(f"%{search}%"))
            query = query.where(search_filter)
        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        query = query.order_by(User.created_at.desc())
        
        count_query = select(func.count()).select_from(User)
        if search:
            count_query = count_query.where(search_filter)
        if role:
            count_query = count_query.where(User.role == role)
        if is_active is not None:
            count_query = count_query.where(User.is_active == is_active)
        
        total = await self._db.scalar(count_query)
        
        query = query.offset(skip).limit(per_page)
        result = await self._db.execute(query)
        users = result.scalars().all()
        
        data = [
            {
                "id": str(u.id),
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "role": u.role,
                "is_active": u.is_active,
                "location": u.location,
                "phone": u.phone,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "updated_at": u.updated_at.isoformat() if u.updated_at else None
            }
            for u in users
        ]
        return UserListResult(
            data=data,
            total=total or 0,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page if per_page > 0 else 0
        )
    
    async def get_user_details(self, user_id: UUID) -> dict:
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        books_count = await self._db.scalar(select(func.count()).select_from(UserBook).where(UserBook.user_id == user_id))
        borrowed_count = await self._db.scalar(select(func.count()).select_from(Loan).where(Loan.borrower_id == user_id))
        lent_count = await self._db.scalar(select(func.count()).select_from(Loan).where(Loan.lender_id == user_id))
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "location": user.location,
            "phone": user.phone,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "stats": {
                "books_count": books_count or 0,
                "borrowed_count": borrowed_count or 0,
                "lent_count": lent_count or 0
            }
        }
    
    async def update_user_role(self, user_id: UUID, new_role: str, current_admin_id: UUID) -> dict:
        if user_id == current_admin_id:
            raise SelfModificationException("role")
        if new_role not in ["reader", "admin"]:
            raise InvalidRoleException(new_role)
        
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        await self._user_repo.update(user, {"role": new_role})
        
        logger.info(f"Admin {current_admin_id} changed role of {user_id} to {new_role}")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role
        }
    
    async def reset_user_password(self, user_id: UUID, current_admin_id: UUID) -> dict:
        if user_id == current_admin_id:
            raise SelfModificationException("password")
        
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        temp_password = secrets.token_urlsafe(12)
        hashed = get_password_hash(temp_password)
        
        await self._user_repo.update(user, {"hashed_password": hashed})
        
        logger.info(f"Admin {current_admin_id} reset password for user {user_id}")
        
        return {
            "message": "Hasło zresetowane",
            "temp_password": temp_password 
        }
    
    async def deactivate_user(self, user_id: UUID, current_admin_id: UUID) -> dict:
        if user_id == current_admin_id:
            raise SelfModificationException("deactivate")
        
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        await self._user_repo.update(user, {"is_active": False})
        
        logger.info(f"Admin {current_admin_id} deactivated user {user_id}")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "is_active": False
        }
    
    async def activate_user(self, user_id: UUID, current_admin_id: UUID) -> dict:
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        await self._user_repo.update(user, {"is_active": True})
        
        logger.info(f"Admin {current_admin_id} activated user {user_id}")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "is_active": True
        }
    
    async def delete_user(self, user_id: UUID, current_admin_id: UUID, hard_delete: bool = False) -> None:
        if user_id == current_admin_id:
            raise SelfModificationException("delete")

        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        if hard_delete:
            await self._user_repo.delete(user_id)
            logger.info(f"Admin {current_admin_id} HARD deleted user {user_id}")
        else:
            await self._user_repo.update(user, {"is_active": False})
            logger.info(f"Admin {current_admin_id} SOFT deleted (deactivated) user {user_id}")
