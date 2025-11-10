from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from .services import TokenService, EmailService, AsyncRequestService
from src.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/swaggerlogin")

def get_email_service() -> EmailService:
    return EmailService()


def get_request_service() -> AsyncRequestService:
    return AsyncRequestService()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    """Returns the email of the current user logged in."""
    return TokenService.verify_token(token)