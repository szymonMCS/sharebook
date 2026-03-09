from typing import AsyncGenerator, Optional
from uuid import UUID
from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import get_async_session
from database.models import User
from database.repositories.user_repository import UserRepository
from src.core.token_blacklist import is_token_revoked
from src.core.constants import ACCESS_TOKEN_COOKIE, CSRF_HEADER_NAME, CSRF_TOKEN_COOKIE
from src.core.security import decode_token, verify_csrf_token
from src.core.exceptions import (
    AuthenticationException,
    NotAuthorizedException,
    CSRFTokenMissingException,
    CSRFTokenInvalidException,
    InactiveUserException,
)
from src.services.interfaces.auth import IAuthService, ITokenService
from src.services.interfaces.books import IBookService, IUserBookService
from src.services.interfaces.loans import ILoanService, ILoanRequestService
from src.services.interfaces.messages import IMessageService
from src.services.factories import ServiceFactory, RepositoryFactory


security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


get_db_session = get_db


def get_service_factory(db: AsyncSession = Depends(get_db)) -> ServiceFactory:
    return ServiceFactory(db=db)

def get_repository_factory(db: AsyncSession = Depends(get_db)) -> RepositoryFactory:
    return RepositoryFactory(db=db)

def get_auth_service(factory: ServiceFactory = Depends(get_service_factory)) -> IAuthService:
    return factory.create_auth_service()

def get_book_service(factory: ServiceFactory = Depends(get_service_factory)) -> IBookService:
    return factory.create_book_service()

def get_user_book_service(factory: ServiceFactory = Depends(get_service_factory)) -> IUserBookService:
    return factory.create_user_book_service()

def get_loan_service(factory: ServiceFactory = Depends(get_service_factory)) -> ILoanService:
    return factory.create_loan_service()

def get_loan_request_service(factory: ServiceFactory = Depends(get_service_factory)) -> ILoanRequestService:
    return factory.create_loan_request_service()

def get_message_service(factory: ServiceFactory = Depends(get_service_factory)) -> IMessageService:
    return factory.create_message_service()

def get_token_service(factory: ServiceFactory = Depends(get_service_factory)) -> ITokenService:
    return factory.create_token_service()

async def get_cover_service():
    from src.services.cover import get_cover_service as get_cs
    return await get_cs()

async def extract_token_from_request(request: Request) -> Optional[str]:
    return request.cookies.get(ACCESS_TOKEN_COOKIE)

def validate_token_payload(token: str) -> Optional[dict]:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    return payload

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = await extract_token_from_request(request)
    if not token:
        raise AuthenticationException("Missing token")
    if is_token_revoked(token):
        raise AuthenticationException("Token has been revoked")

    payload = validate_token_payload(token)
    if not payload:
        raise AuthenticationException("Invalid token")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException("Invalid token payload")

    user_id = UUID(user_id_str)
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)

    if not user:
        raise AuthenticationException("User not found")
    if not user.is_active:
        raise InactiveUserException()
    return user

get_current_active_user = get_current_user

def _verify_csrf_internal(request: Request) -> None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    header_token = request.headers.get(CSRF_HEADER_NAME)
    cookie_token = request.cookies.get(CSRF_TOKEN_COOKIE)

    if not header_token:
        raise CSRFTokenMissingException()
    if not cookie_token:
        raise CSRFTokenInvalidException()
    if not verify_csrf_token(header_token, cookie_token):
        raise CSRFTokenInvalidException()

async def verify_csrf_protection(request: Request, current_user: User = Depends(get_current_active_user)) -> User:
    _verify_csrf_internal(request)
    return current_user

async def get_current_user_optional(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[User]:
    try:
        return await get_current_user(request, db)
    except AuthenticationException:
        return None

async def verify_csrf_token_only(request: Request) -> None:
    _verify_csrf_internal(request)

async def get_current_active_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise NotAuthorizedException("Admin access required")
    return current_user
