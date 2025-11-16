from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from .services import TokenService, EmailService, AsyncRequestService
from src.users.schemas import UserInDB
from src.users.dependencies import UserService, get_user_service
from src.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/swaggerlogin")

def get_email_service() -> EmailService:
    return EmailService()


def get_request_service() -> AsyncRequestService:
    return AsyncRequestService()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserInDB:
    """Returns the email of the current user logged in."""
    email = TokenService.verify_token(token)
    return await user_service.get_by_email(email)