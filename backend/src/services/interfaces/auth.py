"""Auth-related interfaces."""
from abc import ABC, abstractmethod
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.user import UserCreate, UserResponse, UserUpdate, UserProfileResponse


class IAuthService(ABC):
    """Main interface for authentication and user management."""

    @abstractmethod
    async def register(self, user: "UserCreate") -> "UserResponse": ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> "UserResponse | None": ...

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> "UserResponse": ...

    @abstractmethod
    async def verify_user_exists(self, email: str) -> bool: ...

    @abstractmethod
    async def authenticate(self, email: str, password: str) -> "UserResponse | None": ...

    @abstractmethod
    async def update_profile(self, user_id: UUID, data: "UserUpdate") -> "UserResponse": ...

    @abstractmethod
    async def get_profile(self, user_id: UUID) -> "UserProfileResponse": ...


class ITokenService(ABC):
    """Service for generating and validating JWT tokens."""

    @abstractmethod
    def generate_token_pair(self, user_id: UUID) -> tuple[str, str, str]:
        """Generate access token, refresh token, and CSRF token.

        Returns:
            Tuple of (access_token, refresh_token, csrf_token)
        """
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        """Refresh access token using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            Tuple of (new_access_token, new_csrf_token)
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict | None:
        """Decode and validate a token.

        Args:
            token: The JWT token to decode

        Returns:
            Decoded token payload or None if invalid
        """
        pass
