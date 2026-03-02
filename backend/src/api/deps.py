from typing import AsyncGenerator, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import get_async_session
from database.models import User
from database.repositories.user_repository import UserRepository
from src.core.constants import (
    ACCESS_TOKEN_COOKIE,
    CSRF_HEADER_NAME,
    CSRF_TOKEN_COOKIE,
    ERROR_CSRF_TOKEN_INVALID,
    ERROR_CSRF_TOKEN_MISSING,
    ERROR_INACTIVE_USER,
    ERROR_INVALID_TOKEN,
    ERROR_MISSING_TOKEN,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    WWW_AUTHENTICATE_HEADER,
)
from src.core.security import decode_token, verify_csrf_token
from src.services.interfaces import (
    IAuthService,
    IUserService,
    IRegistrationService,
    ITokenService,
    IBookCatalogService,
    ILibraryManagementService,
    ICommunityBookService,
    IBookImportService,
    ILoanService,
    ILoanRequestService,
)
from src.services.factories import ServiceFactory, RepositoryFactory


security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


def get_repository_factory():
    return RepositoryFactory

def get_service_factory(db: AsyncSession = Depends(get_db)) -> ServiceFactory:
    return ServiceFactory(db=db)

def get_auth_service(factory: ServiceFactory = Depends(get_service_factory)) -> IAuthService:
    return factory.create_auth_service()

def get_user_service(factory: ServiceFactory = Depends(get_service_factory)) -> IUserService:
    return factory.create_user_service()

def get_registration_service(factory: ServiceFactory = Depends(get_service_factory)) -> IRegistrationService:
    return factory.create_registration_service()

def get_token_service(factory: ServiceFactory = Depends(get_service_factory)) -> ITokenService:
    return factory.create_token_service()

def get_book_catalog_service(factory: ServiceFactory = Depends(get_service_factory)) -> IBookCatalogService:
    return factory.create_book_catalog_service()

def get_library_management_service(factory: ServiceFactory = Depends(get_service_factory)) -> ILibraryManagementService:
    return factory.create_library_management_service()

def get_community_book_service(factory: ServiceFactory = Depends(get_service_factory)) -> ICommunityBookService:
    return factory.create_community_book_service()

def get_book_import_service(factory: ServiceFactory = Depends(get_service_factory)) -> IBookImportService:
    return factory.create_book_import_service()

def get_loan_service(factory: ServiceFactory = Depends(get_service_factory)) -> ILoanService:
    return factory.create_loan_service()

def get_loan_request_service(factory: ServiceFactory = Depends(get_service_factory)) -> ILoanRequestService:
    return factory.create_loan_request_service()

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
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=ERROR_MISSING_TOKEN,
            headers={"WWW-Authenticate": WWW_AUTHENTICATE_HEADER},
        )

    payload = validate_token_payload(token)
    if not payload:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_TOKEN,
            headers={"WWW-Authenticate": WWW_AUTHENTICATE_HEADER},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_TOKEN,
            headers={"WWW-Authenticate": WWW_AUTHENTICATE_HEADER},
        )

    user_id = UUID(user_id_str)
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_TOKEN,
            headers={"WWW-Authenticate": WWW_AUTHENTICATE_HEADER},
        )

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=ERROR_INACTIVE_USER,
        )
    return current_user

async def verify_csrf_protection(request: Request, current_user: User = Depends(get_current_active_user)) -> User:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return current_user

    header_token = request.headers.get(CSRF_HEADER_NAME)
    cookie_token = request.cookies.get(CSRF_TOKEN_COOKIE)

    if not header_token:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=ERROR_CSRF_TOKEN_MISSING,
        )

    if not cookie_token:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=ERROR_CSRF_TOKEN_INVALID,
        )

    if not verify_csrf_token(header_token, cookie_token):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=ERROR_CSRF_TOKEN_INVALID,
        )

    return current_user

async def get_current_user_optional(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[User]:
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None

async def verify_csrf_token_only(request: Request) -> None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    header_token = request.headers.get(CSRF_HEADER_NAME)
    cookie_token = request.cookies.get(CSRF_TOKEN_COOKIE)

    if not header_token:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=ERROR_CSRF_TOKEN_MISSING,
        )

    if not cookie_token:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=ERROR_CSRF_TOKEN_INVALID,
        )

    if not verify_csrf_token(header_token, cookie_token):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=ERROR_CSRF_TOKEN_INVALID,
        )
