from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.api.deps import (
    get_auth_service,
    get_registration_service,
    get_token_service,
    verify_csrf_protection,
    verify_csrf_token_only,
)
from src.core.constants import (
    ACCESS_TOKEN_COOKIE,
    REFRESH_TOKEN_COOKIE,
    CSRF_TOKEN_COOKIE,
    ACCESS_TOKEN_MAX_AGE,
    REFRESH_TOKEN_MAX_AGE,
    CSRF_TOKEN_MAX_AGE,
    MSG_LOGIN_SUCCESS,
    MSG_LOGOUT_SUCCESS,
    MSG_REGISTER_SUCCESS,
    MSG_TOKEN_REFRESHED,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    ERROR_INVALID_CREDENTIALS,
)
from src.core.security import get_cookie_config, get_csrf_cookie_config
from src.core.exceptions import ShareBookException
from src.schemas.user import UserCreate
from src.services.interfaces import IAuthService, IRegistrationService, ITokenService
from database.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])

def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str) -> None:
    response.set_cookie(ACCESS_TOKEN_COOKIE, access_token, max_age=ACCESS_TOKEN_MAX_AGE, **get_cookie_config())
    response.set_cookie(REFRESH_TOKEN_COOKIE, refresh_token, max_age=REFRESH_TOKEN_MAX_AGE, **get_cookie_config())
    response.set_cookie(CSRF_TOKEN_COOKIE, csrf_token, max_age=CSRF_TOKEN_MAX_AGE, **get_csrf_cookie_config())

def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/")
    response.delete_cookie(CSRF_TOKEN_COOKIE, path="/")

@router.post("/register", response_model=dict, status_code=HTTP_201_CREATED)
async def register(
    request: Request,
    response: Response,
    user_data: UserCreate,
    registration_service: IRegistrationService = Depends(get_registration_service),
    token_service: ITokenService = Depends(get_token_service)
):
    try:
        user = await registration_service.register(user_data)
    except ShareBookException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)

    access_token, refresh_token, csrf_token = token_service.generate_token_pair(user.id)
    set_auth_cookies(response, access_token, refresh_token, csrf_token)

    from src.core.response import APIResponse
    return APIResponse.ok(data={"user": user.model_dump()}, message=MSG_REGISTER_SUCCESS)

@router.post("/login", response_model=dict)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: IAuthService = Depends(get_auth_service),
    token_service: ITokenService = Depends(get_token_service)
):
    user = await auth_service.authenticate(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token, csrf_token = token_service.generate_token_pair(user.id)
    set_auth_cookies(response, access_token, refresh_token, csrf_token)

    return APIResponse.ok(data={"user": user.model_dump()}, message=MSG_LOGIN_SUCCESS)

@router.post("/logout", status_code=HTTP_204_NO_CONTENT)
async def logout(response: Response, request: Request, current_user: User = Depends(verify_csrf_protection)):
    clear_auth_cookies(response)
    return None

@router.post("/refresh", response_model=dict)
async def refresh(
    response: Response, 
    request: Request, 
    token_service: ITokenService = Depends(get_token_service),
    _: None = Depends(verify_csrf_token_only)
):
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)

    if not refresh_token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        new_access_token, new_csrf_token = await token_service.refresh_access_token(
            refresh_token
        )
    except ShareBookException as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    response.set_cookie(ACCESS_TOKEN_COOKIE, new_access_token, max_age=ACCESS_TOKEN_MAX_AGE, **get_cookie_config())
    response.set_cookie(CSRF_TOKEN_COOKIE, new_csrf_token, max_age=CSRF_TOKEN_MAX_AGE, **get_csrf_cookie_config())
    return APIResponse.ok(message=MSG_TOKEN_REFRESHED)
