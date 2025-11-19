from fastapi import Depends, Request
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
    request: Request,
) -> str:
    """Returns the email of the current user logged in."""
    token = request.cookies.get("access_token", "NO_TOKEN")
    return TokenService.verify_token(token)