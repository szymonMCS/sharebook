from fastapi import Response
from src.core.constants import (
    ACCESS_TOKEN_COOKIE,
    REFRESH_TOKEN_COOKIE,
    CSRF_TOKEN_COOKIE,
    ACCESS_TOKEN_MAX_AGE,
    REFRESH_TOKEN_MAX_AGE,
    CSRF_TOKEN_MAX_AGE,
)
from src.core.security import get_cookie_config, get_csrf_cookie_config


class CookieService:
    def set_auth_cookies(self, response: Response, access_token: str, refresh_token: str, csrf_token: str) -> None:
        response.set_cookie(ACCESS_TOKEN_COOKIE, access_token, max_age=ACCESS_TOKEN_MAX_AGE, **get_cookie_config())
        response.set_cookie(REFRESH_TOKEN_COOKIE, refresh_token, max_age=REFRESH_TOKEN_MAX_AGE, **get_cookie_config())
        response.set_cookie(CSRF_TOKEN_COOKIE, csrf_token, max_age=CSRF_TOKEN_MAX_AGE, **get_csrf_cookie_config())
    
    def set_refresh_cookies(self, response: Response, access_token: str, csrf_token: str) -> None:
        response.set_cookie(ACCESS_TOKEN_COOKIE, access_token, max_age=ACCESS_TOKEN_MAX_AGE, **get_cookie_config())
        response.set_cookie(CSRF_TOKEN_COOKIE, csrf_token, max_age=CSRF_TOKEN_MAX_AGE, **get_csrf_cookie_config())
    
    def clear_auth_cookies(self, response: Response) -> None:
        response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
        response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/")
        response.delete_cookie(CSRF_TOKEN_COOKIE, path="/")
