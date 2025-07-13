from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
from redis.asyncio import Redis
from .repositories import OTPRepository, AuthenticationRepository
from .services import OTPService, AuthenticationService
from src.core.config import settings
from src.core.database import get_db
from src.users.schemas import UserOut
from src.users.repositories import UserRepository
from src.users.dependencies import get_user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/swaggerlogin")

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
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> OTPService:
    
    """Returns otp service dependency"""
    return OTPService(otp_repo, user_repo)

# Authentication
def get_authentication_repository(db: Annotated[Session, Depends(get_db)]) -> AuthenticationRepository:
    """Returns authentication repository dependency."""
    return AuthenticationRepository(db)

def get_authentication_service(
    authentication_repo: Annotated[AuthenticationRepository, Depends(get_authentication_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> AuthenticationService:
    """Returns authentication service dependency."""
    return AuthenticationService(authentication_repo, user_repo, otp_service)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> UserOut:
    """Returns the current user who is logged in."""
    return await auth_service.get_user_from_token(token)



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

