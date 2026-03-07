from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfileResponse


class IAuthService(ABC):
    @abstractmethod
    async def authenticate(self, email: str, password: str) -> Optional[UserResponse]:
        pass


class IUserService(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserResponse:
        pass
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        pass
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass
    @abstractmethod
    async def update(self, user_id: UUID, user_update: UserUpdate) -> UserResponse:
        pass
    @abstractmethod
    async def get_profile(self, user_id: UUID) -> UserProfileResponse:
        pass


class IRegistrationService(ABC):
    @abstractmethod
    async def register(self, user_data: UserCreate) -> UserResponse:
        pass


class IPasswordService(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        pass
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        pass


class ITokenService(ABC):
    @abstractmethod
    def generate_token_pair(self, user_id: UUID) -> tuple[str, str, str]:
        pass
    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        pass
    @abstractmethod
    def decode_token(self, token: str) -> Optional[dict]:
        pass
