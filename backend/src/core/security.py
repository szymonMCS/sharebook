from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
import secrets
from jose import JWTError, jwt

from src.config import settings
from src.core.constants import (
    ACCESS_TOKEN_EXPIRE_DELTA,
    REFRESH_TOKEN_EXPIRE_DELTA,
    BCRYPT_ROUNDS,
)


def _to_bytes(text: str) -> bytes:
    return text.encode('utf-8')[:72]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_to_bytes(plain_password), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode('utf-8')

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, cookie_token: str) -> bool:
    if not token or not cookie_token:
        return False
    return secrets.compare_digest(token, cookie_token)

def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    
    to_encode.update({
        "exp": now + ACCESS_TOKEN_EXPIRE_DELTA,
        "iat": now,
        "type": "access"
    })
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    
    to_encode.update({
        "exp": now + REFRESH_TOKEN_EXPIRE_DELTA,
        "iat": now,
        "type": "refresh"
    })
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None