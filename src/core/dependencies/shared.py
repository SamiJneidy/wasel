from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from src.auth.exceptions import InvalidTokenException
from src.core.enums import TokenScope
from src.auth.services.token_service import TokenService
from src.users.schemas import UserInDB
from src.auth.dependencies.token_deps import TokenService, get_token_service
from src.users.dependencies import UserService, get_user_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/swaggerlogin")

async def get_current_user(
    request: Request,
    dummy_token: Annotated[str, Depends(oauth2_scheme)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserInDB:
    """Returns the email of the current user logged in."""
    token = request.cookies.get("access_token", "NO_TOKEN")
    email = token_service.verify_token(token)
    return await user_service.get_by_email(email)

async def get_current_user_from_sign_up_complete_token(
    request: Request,
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserInDB:
    """Returns the email of the current user waiting for sign up complete step."""
    token = request.cookies.get("sign_up_complete_token", "NO_TOKEN")
    payload = token_service.decode_token(token)
    if payload["scope"] != TokenScope.SIGN_UP_COMPLETE:
        raise InvalidTokenException()
    return await user_service.get_by_email(payload["sub"])