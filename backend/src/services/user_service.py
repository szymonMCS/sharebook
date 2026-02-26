import logging
from uuid import UUID
from typing import Optional
from src.services.interfaces import IUserService
from database.repositories.interfaces import IUserRepository
from src.schemas.user import UserUpdate, UserResponse, UserProfileResponse
from src.core.exceptions import UserNotFoundException

logger = logging.getLogger(__name__)


class UserService(IUserService):
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    async def get_by_id(self, user_id: UUID) -> UserResponse:
        db_user = await self._user_repo.get(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)
        return UserResponse.model_validate(db_user)

    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        db_user = await self._user_repo.get_by_email(email)
        if not db_user:
            return None
        return UserResponse.model_validate(db_user)

    async def exists_by_email(self, email: str) -> bool:
        return await self._user_repo.email_exists(email)

    async def update(self, user_id: UUID, user_update: UserUpdate) -> UserResponse:
        db_user = await self._user_repo.get(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)

        updated_user = await self._user_repo.update(
            db_obj=db_user,
            obj_in=user_update.model_dump(exclude_unset=True)
        )
        
        logger.info(f"User updated: {user_id}")
        return UserResponse.model_validate(updated_user)

    async def get_profile(self, user_id: UUID) -> UserProfileResponse:
        db_user = await self._user_repo.get(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)

        # TODO: Get actual books count from repository
        books_count = 0

        return UserProfileResponse(
            id=db_user.id,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            role=db_user.role,
            is_active=db_user.is_active,
            location=db_user.location,
            phone=db_user.phone,
            bio=db_user.bio,
            created_at=db_user.created_at,
            books_count=books_count
        )
