import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Request, Response
from src.core.config import settings
from ..schemas.token_schemas import AccessToken, RefreshToken, SignUpCompleteToken, UserInviteToken
from ..repositories.token_repo import TokenRepository
from ...auth.exceptions import InvalidTokenException


class TokenService:
    
    def __init__(self, token_repo: TokenRepository):
        self.token_repo = token_repo

    def _create_token(self, payload: dict) -> str:
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def decode_token(self, token: str) -> dict:  
        try:
            payload_dict: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload_dict.get("sub")
            if not user_id:
                raise InvalidTokenException()
            try:
                payload_dict["sub"] = int(payload_dict["sub"])
                payload_dict["branch_id"] = int(payload_dict["branch_id"])
                payload_dict["organization_id"] = int(payload_dict["organization_id"])
            except Exception as e:
                raise InvalidTokenException()
            return payload_dict
        except jwt.InvalidTokenError:
            raise InvalidTokenException()

    def create_access_token(self, token: AccessToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
        payload = token.model_dump()
        return self._create_token(payload)


    def create_refresh_token(self, token: RefreshToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
        payload = token.model_dump()
        return self._create_token(payload)


    def create_sign_up_complete_token(self, token: SignUpCompleteToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(days=settings.SIGN_UP_COMPLETE_EXPIRATION_DAYS)
        payload = token.model_dump()
        return self._create_token(payload)


    def create_user_invitation_token(self, token: UserInviteToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(days=settings.USER_INVITATION_TOKEN_EXPIRATION_MINUTES)
        payload = token.model_dump()
        return self._create_token(payload)
    

    def set_token_cookies(self, response: Response, access_token: str, refresh_token: str) -> None:
        self.set_access_token_cookie(response, access_token)
        self.set_refresh_token_cookie(response, refresh_token)
    

    def set_access_token_cookie(self, request: Request, response: Response, token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.ENVIRONMENT == "PRODUCTION" and not is_local
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
            path="/"
        )


    def set_refresh_token_cookie(self, request: Request, response: Response, token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.ENVIRONMENT == "PRODUCTION" and not is_local
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
            path="/",
        )

    
    def set_sign_up_complete_token_cookie(self, request: Request, response: Response, token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.ENVIRONMENT == "PRODUCTION" and not is_local
        response.set_cookie(
            key="sign_up_complete_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.SIGN_UP_COMPLETE_EXPIRATION_DAYS * 24 * 60 * 60,
            path="/",
        )
