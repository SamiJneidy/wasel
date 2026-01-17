from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .schemas import UserOut
from .repositories import UserRepository
from .services import UserService
from src.core.database import get_db
from src.organizations.dependencies import OrganizationService, get_organization_service
from src.core.dependencies.email_deps import EmailService, get_email_service
from src.auth.dependencies.token_deps import TokenService, get_token_service
from src.authorization.dependencies import AuthorizationService, get_authorization_service

def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    """Returns user repository dependency."""
    return UserRepository(db)

def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> UserService:
    """Returns user service dependency"""
    return UserService(user_repo, email_service, token_service, organization_service, authorization_service)
