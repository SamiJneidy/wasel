import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Request, Response
from src.core.config import settings
from ..repositories.token_repo import TokenRepository
from ...auth.exceptions import InvalidTokenException


class TokenService:
    
    def __init__(self, token_repo: TokenRepository):
        self.token_repo = token_repo

    def create_token(self, payload: dict) -> str:
        """Creates an access token."""
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


    def verify_token(self, token: str) -> str:
        """Verifies if a token is valid or not and returns the user's email if the token was valid."""   
        try:
            payload_dict: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload_dict.get("sub")
            if not email:
                raise InvalidTokenException()
            return email
        except jwt.InvalidTokenError:
            raise InvalidTokenException()


    def set_token_cookies(self, response: Response, access_token: str, refresh_token: str) -> None:
        self.set_access_token_cookie(response, access_token)
        self.set_refresh_token_cookie(response, refresh_token)
    

    def set_access_token_cookie(self, request: Request, response: Response, access_token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.ENVIRONMENT == "PRODUCTION" and not is_local
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
            path="/"
        )


    def set_refresh_token_cookie(self, request: Request, response: Response, refresh_token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.ENVIRONMENT == "PRODUCTION" and not is_local
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
            path="/",
        )
