from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from database.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserResponse


class UserService:
    def __init__(self, db: AsyncSession, repository: UserRepository | None = None):
        self.db = db
        self.repository = repository or UserRepository(db)
    
    def _hash_password(self, password: str) -> str:
        from src.core.security import get_password_hash
        return get_password_hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        from src.core.security import verify_password
        return verify_password(plain_password, hashed_password)
    
    async def register(self, user_data: UserCreate) -> User:
        if await self.repository.email_exists(user_data.email):
            raise ValueError(f"Użytkownik z emailem {user_data.email} już istnieje")
        
        hashed_password = self._hash_password(user_data.password)
        
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            location=user_data.location,
            phone=user_data.phone,
        )
        
        return await self.repository.create(db_user)
    
    async def get_by_id(self, user_id: UUID) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")
        return user
    
    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)
    
    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.hashed_password):
            return None
        return user
