import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Response
from src.core.config import settings
from ...auth.exceptions import InvalidTokenException


class TokenService:
    
    @classmethod
    def create_access_token(self, payload: dict) -> str:
        """Creates an access token."""
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @classmethod
    def create_refresh_token(self, payload: dict) -> str:
        """Creates a refresh token."""
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


    @classmethod
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


    @classmethod
    def refresh(self, refresh_token: str, payload: dict) -> str:
        """Refreshes an expired access token using a valid refresh token and returns the new access token."""
        email = self.verify_token(refresh_token)
        return self.create_access_token(payload)


    @classmethod
    def set_token_cookies(self, access_token: str, refresh_token: str, response: Response, refresh_path: str) -> None:
        """Sets the refresh token cookie. The cookie will be set based on the current environment. The 'path' argument will not be used in development environment."""
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True if settings.ENVIRONMENT == "PRODUCTION" else False,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True if settings.ENVIRONMENT == "PRODUCTION" else False,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
            path=refresh_path if settings.ENVIRONMENT == "PRODUCTION" else "/"
        )