import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Response
from src.core.config import settings
from ...auth.exceptions import InvalidTokenException


class TokenService:
    
    def __init__(self):
        pass

    def create_token(self, payload: dict) -> str:
        """Creates an access token."""
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # @classmethod
    # def create_refresh_token(self, payload: dict) -> str:
    #     """Creates a refresh token."""
    #     return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


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
    

    def set_access_token_cookie(self, response: Response, access_token: str) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True if settings.ENVIRONMENT == "PRODUCTION" else False,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
            path="/"
        )


    def set_refresh_token_cookie(self, response: Response, refresh_token: str) -> None:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True if settings.ENVIRONMENT == "PRODUCTION" else False,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
            path="/"
        )
