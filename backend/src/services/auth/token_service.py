"""Token service for authentication."""
from uuid import UUID
from typing import Optional
from src.services.interfaces.auth import ITokenService
from src.core.security import create_access_token, create_refresh_token, decode_token, generate_csrf_token
from src.core.token_blacklist import is_token_revoked
from src.core.exceptions import ShareBookException


class TokenService(ITokenService):
    """Service for generating and validating JWT tokens."""

    def generate_token_pair(self, user_id: UUID) -> tuple[str, str, str]:
        """Generate access token, refresh token, and CSRF token.
        
        Returns:
            Tuple of (access_token, refresh_token, csrf_token)
        """
        access_token = create_access_token({"sub": str(user_id)})
        refresh_token = create_refresh_token({"sub": str(user_id)})
        csrf_token = generate_csrf_token()
        return access_token, refresh_token, csrf_token

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Tuple of (new_access_token, new_csrf_token)
            
        Raises:
            ShareBookException: If token is invalid or revoked
        """
        if is_token_revoked(refresh_token):
            raise ShareBookException("Token has been revoked", status_code=401)

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ShareBookException("Invalid refresh token", status_code=401)

        user_id = payload.get("sub")
        if not user_id:
            raise ShareBookException("Invalid token payload", status_code=401)

        new_access_token = create_access_token({"sub": user_id})
        new_csrf_token = generate_csrf_token()
        return new_access_token, new_csrf_token

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and validate a token.
        
        Args:
            token: The JWT token to decode
            
        Returns:
            Decoded token payload or None if invalid
        """
        return decode_token(token)
