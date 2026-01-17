from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from redis.asyncio import Redis
from .otp_deps import get_otp_service, OTPService
from .token_deps import get_token_service, TokenService
from ..repositories.auth_repo import AuthRepository
from ..services.auth_service import AuthService 
from src.core.dependencies.email_deps import get_email_service
from src.core.config import settings
from src.core.database import get_db
from src.organizations.dependencies import OrganizationService, get_organization_service
from src.users.dependencies import UserService, get_user_service
from src.authorization.dependencies import AuthorizationService, get_authorization_service
from src.core.services import EmailService

async def get_redis():
    redis = Redis.from_url(settings.REDIS_URL)
    try:
        yield redis
    finally:
        await redis.close()

def get_auth_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthRepository:
    """Returns authentication repository dependency."""
    return AuthRepository(db)


def get_auth_service(
    authentication_repo: Annotated[AuthRepository, Depends(get_auth_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)]
) -> AuthService:
    """Returns authentication service dependency."""
    return AuthService(authentication_repo, token_service, user_service, otp_service, email_service, organization_service, authorization_service)
