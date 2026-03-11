from uuid import UUID
import logging
from database.interfaces import IUserRepository, IBookRepository
from src.schemas.user import UserCreate, UserResponse, UserCreateInternal, UserUpdate, UserProfileResponse
from src.core.exceptions import NotFoundException, DuplicateEmailException
from src.core.security import get_password_hash, verify_password
from src.services.interfaces.auth import IAuthService

logger = logging.getLogger(__name__)


class AuthService(IAuthService):
    def __init__(self, repository: IUserRepository, book_repo: IBookRepository | None = None):
        self._repo = repository
        self._book_repo = book_repo

    async def register(self, user: UserCreate) -> UserResponse:
        existing = await self._repo.get_by_email(user.email)
        if existing:
            raise DuplicateEmailException(user.email)

        hashed_password = get_password_hash(user.password)

        internal_data = UserCreateInternal(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            location=user.location
        )
        db_user = await self._repo.create_user(
            email=internal_data.email,
            hashed_password=internal_data.hashed_password,
            first_name=internal_data.first_name,
            last_name=internal_data.last_name,
            role=internal_data.role,
            location=internal_data.location
        )
        
        logger.info(f"User registered: {db_user.id} with email {user.email}")
        
        return UserResponse.model_validate(db_user)

    async def get_user_by_email(self, email: str) -> UserResponse | None:
        db_user = await self._repo.get_by_email(email)
        if not db_user:
            return None
        return UserResponse.model_validate(db_user)

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        db_user = await self._repo.get_by_id(user_id)
        if not db_user:
            raise NotFoundException("User", str(user_id))
        return UserResponse.model_validate(db_user)

    async def verify_user_exists(self, email: str) -> bool:
        existing = await self._repo.get_by_email(email)
        return existing is not None
    
    async def authenticate(self, email: str, password: str) -> UserResponse | None:
        db_user = await self._repo.get_by_email(email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        
        logger.info(f"User authenticated: {db_user.id}")
        
        return UserResponse.model_validate(db_user)
    
    async def update_profile(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        existing = await self._repo.get_by_id(user_id)
        if not existing:
            raise NotFoundException("User", str(user_id))
        
        update_dict = data.model_dump(exclude_unset=True)
        updated = await self._repo.update(existing, update_dict)
        
        logger.info(f"User profile updated: {user_id}")
        
        return UserResponse.model_validate(updated)
    
    async def get_profile(self, user_id: UUID) -> UserProfileResponse:
        db_user = await self._repo.get_by_id(user_id)
        if not db_user:
            raise NotFoundException("User", str(user_id))
        
        books_count = 0
        if self._book_repo:
            user_books = await self._book_repo.get_by_owner(user_id, skip=0, limit=10000)
            books_count = len(user_books)
        
        return UserProfileResponse(
            id=db_user.id,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            role=db_user.role,
            is_active=db_user.is_active,
            bio=db_user.bio,
            location=db_user.location,
            phone=db_user.phone,
            avatar_url=db_user.avatar_url,
            books_count=books_count
        )
