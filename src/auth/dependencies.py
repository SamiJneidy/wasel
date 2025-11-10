from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
from redis.asyncio import Redis

from .repositories import OTPRepository, AuthenticationRepository
from .services import AuthService, OTPService
from src.core.dependencies import get_email_service, get_current_user, oauth2_scheme
from src.core.config import settings
from src.core.database import get_db
from src.users.schemas import UserOut
from src.users.repositories import UserRepository
from src.organizations.dependencies import OrganizationService, get_organization_service
from src.users.dependencies import get_user_service
from src.core.services import EmailService

# Redis
async def get_redis():
    redis = Redis.from_url(settings.REDIS_URL)
    try:
        yield redis
    finally:
        await redis.close()


# OTP
def get_otp_repository(db: Annotated[Session, Depends(get_db)]) -> OTPRepository:
    """Returns otp repository dependency"""
    return OTPRepository(db)


def get_otp_service(
    otp_repo: Annotated[OTPRepository, Depends(get_otp_repository)],
) -> OTPService:
    
    """Returns otp service dependency"""
    return OTPService(otp_repo)


# Auth
def get_auth_repository(db: Annotated[Session, Depends(get_db)]) -> AuthenticationRepository:
    """Returns authentication repository dependency."""
    return AuthenticationRepository(db)


def get_auth_service(
    authentication_repo: Annotated[AuthenticationRepository, Depends(get_auth_repository)],
    user_service: Annotated[UserRepository, Depends(get_user_service)],
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> AuthService:
    """Returns authentication service dependency."""
    return AuthService(authentication_repo, user_service, otp_service, email_service, organization_service)



# async def get_current_user(
#     token: Annotated[str, Depends(oauth2_scheme)], 
#     auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
# ) -> UserResponse:
#     """Returns the current user from the token."""
#     user = await auth_service.get_user_from_token(token)
#     current_user.set(user)    
#     company = await company_service.get_company_by_id(user.company_id)
#     current_company.set(company)
#     return user
