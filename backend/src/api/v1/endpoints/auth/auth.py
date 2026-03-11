from fastapi import APIRouter, Cookie, Depends, Response, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.api.deps import get_auth_service, get_token_service, verify_csrf_protection, verify_csrf_token_only
from src.core.constants import (
    REFRESH_TOKEN_COOKIE,
    MSG_LOGIN_SUCCESS,
    MSG_REGISTER_SUCCESS,
    MSG_TOKEN_REFRESHED,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
)
from src.core.exceptions import InvalidCredentialsException, AuthenticationException
from src.core.response import APIResponse
from src.schemas.user import UserCreate
from src.services.interfaces.auth import IAuthService, ITokenService
from src.services.auth import CookieService
from src.core.token_blacklist import revoke_token, is_token_revoked
from database.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=dict, status_code=HTTP_201_CREATED)
async def register(
    request: Request,
    response: Response,
    user_data: UserCreate,
    auth_service: IAuthService = Depends(get_auth_service),
    token_service: ITokenService = Depends(get_token_service)
) -> dict:
    user = await auth_service.register(user_data)
    access_token, refresh_token, csrf_token = token_service.generate_token_pair(user.id)
    cookie_service = CookieService()
    cookie_service.set_auth_cookies(response, access_token, refresh_token, csrf_token)
    return APIResponse.ok(data={"user": user.model_dump()}, message=MSG_REGISTER_SUCCESS).model_dump()

@router.post("/login", response_model=dict)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: IAuthService = Depends(get_auth_service),
    token_service: ITokenService = Depends(get_token_service)
) -> dict:
    user = await auth_service.authenticate(form_data.username, form_data.password)

    if not user:
        raise InvalidCredentialsException()

    access_token, refresh_token, csrf_token = token_service.generate_token_pair(user.id)
    cookie_service = CookieService()
    cookie_service.set_auth_cookies(response, access_token, refresh_token, csrf_token)
    return APIResponse.ok(data={"user": user.model_dump()}, message=MSG_LOGIN_SUCCESS).model_dump()


@router.post("/logout", status_code=HTTP_204_NO_CONTENT)
async def logout(response: Response, request: Request, current_user: User = Depends(verify_csrf_protection), refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE)) -> None:
    if refresh_token:
        revoke_token(refresh_token)
    cookie_service = CookieService()
    cookie_service.clear_auth_cookies(response)
    return None

@router.post("/refresh", response_model=dict)
async def refresh(response: Response, request: Request, token_service: ITokenService = Depends(get_token_service), _: None = Depends(verify_csrf_token_only)) -> dict:
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)

    if not refresh_token:
        raise AuthenticationException("Refresh token missing")
    if is_token_revoked(refresh_token):
        raise AuthenticationException("Token has been revoked")

    new_access_token, new_csrf_token = await token_service.refresh_access_token(refresh_token)

    cookie_service = CookieService()
    cookie_service.set_refresh_cookies(response, new_access_token, new_csrf_token)
    return APIResponse.ok(message=MSG_TOKEN_REFRESHED).model_dump()
