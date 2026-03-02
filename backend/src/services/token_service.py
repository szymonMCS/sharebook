from uuid import UUID
from typing import Optional
from src.services.interfaces import ITokenService
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_csrf_token,
)
from src.core.exceptions import RefreshTokenInvalidException, UserNotFoundException
from database.interfaces import IUserRepository


class TokenService(ITokenService):

    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def generate_token_pair(self, user_id: UUID) -> tuple[str, str, str]:
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        csrf_token = generate_csrf_token()

        return access_token, refresh_token, csrf_token

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        payload = self.decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise RefreshTokenInvalidException()

        user_id_str = payload.get("sub")

        if not user_id_str:
            raise RefreshTokenInvalidException()

        user_id = UUID(user_id_str)

        db_user = await self._user_repo.get(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)

        new_access_token = create_access_token(data={"sub": str(user_id)})
        new_csrf_token = generate_csrf_token()

        return new_access_token, new_csrf_token

    def decode_token(self, token: str) -> Optional[dict]:
        return decode_token(token)
