import logging
from typing import Optional
from src.services.interfaces.auth import IAuthService, IPasswordService
from database.interfaces import IUserRepository
from src.schemas.user import UserResponse

logger = logging.getLogger(__name__)


class AuthService(IAuthService):
    def __init__(self, user_repo: IUserRepository, password_service: IPasswordService):
        self._user_repo = user_repo
        self._password_service = password_service

    async def authenticate(self, email: str, password: str) -> Optional[UserResponse]:
        db_user = await self._user_repo.get_by_email(email)
        if not db_user:
            return None

        if not self._password_service.verify(password, db_user.hashed_password):
            return None

        logger.info(f"User authenticated: {db_user.id}")
        return UserResponse.model_validate(db_user)
