import logging
from src.services.interfaces import IRegistrationService, IPasswordService
from database.interfaces import IUserRepository
from src.schemas.user import UserCreate, UserResponse
from src.core.exceptions import DuplicateEmailException

logger = logging.getLogger(__name__)


class RegistrationService(IRegistrationService):
    def __init__(self, user_repo: IUserRepository, password_service: IPasswordService):
        self._user_repo = user_repo
        self._password_service = password_service

    async def register(self, user_data: UserCreate) -> UserResponse:
        if await self._user_repo.email_exists(user_data.email):
            raise DuplicateEmailException(user_data.email)

        hashed_password = self._password_service.hash(user_data.password)

        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['hashed_password'] = hashed_password

        db_user = await self._user_repo.create(user_dict)
        
        logger.info(f"User registered: {db_user.id} with email {user_data.email}")
        
        return UserResponse.model_validate(db_user)
