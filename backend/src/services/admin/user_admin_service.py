import logging
import secrets
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from database.interfaces import IUserRepository, IUserBookRepository, ILoanRepository
from src.core.security import get_password_hash
from src.core.exceptions import (
    UserNotFoundException,
    SelfModificationException,
    InvalidRoleException
)
from src.services.interfaces import IUserAdminService, UserListResult

logger = logging.getLogger(__name__)


class UserAdminService(IUserAdminService):
    def __init__(
        self, 
        db: AsyncSession, 
        user_repo: Optional[IUserRepository] = None,
        user_book_repo: Optional[IUserBookRepository] = None,
        loan_repo: Optional[ILoanRepository] = None
    ):
        self._db = db
        self._user_repo = user_repo
        self._user_book_repo = user_book_repo
        self._loan_repo = loan_repo
        
        if self._user_repo is None:
            from database.repositories.user_repository import UserRepository
            self._user_repo = UserRepository(db)
        if self._user_book_repo is None:
            from database.repositories.user_book_repository import UserBookRepository
            self._user_book_repo = UserBookRepository(db)
        if self._loan_repo is None:
            from database.repositories.loan_repository import LoanRepository
            self._loan_repo = LoanRepository(db)
    
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserListResult:
        skip = (page - 1) * per_page
        
        users, total = await self._user_repo.get_multi_with_filters(
            skip=skip,
            limit=per_page,
            search=search,
            role=role,
            is_active=is_active
        )
        
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
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page if per_page > 0 else 0
        )
    
    async def update_user_role(self, user_id: UUID, new_role: str, current_admin_id: UUID) -> dict:
        if user_id == current_admin_id:
            raise SelfModificationException("role")
        if new_role not in ["reader", "admin"]:
            raise InvalidRoleException(new_role)
        
        user = await self._user_repo.get_by_id(user_id)
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
        
        user = await self._user_repo.get_by_id(user_id)
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
    
    async def delete_user(self, user_id: UUID, current_admin_id: UUID, hard_delete: bool = False) -> None:
        if user_id == current_admin_id:
            raise SelfModificationException("delete")

        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        if hard_delete:
            await self._user_repo.delete(user_id)
            logger.info(f"Admin {current_admin_id} HARD deleted user {user_id}")
        else:
            await self._user_repo.update(user, {"is_active": False})
            logger.info(f"Admin {current_admin_id} SOFT deleted (deactivated) user {user_id}")
