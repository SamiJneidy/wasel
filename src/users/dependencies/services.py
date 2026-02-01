from fastapi import Depends
from typing import Annotated
from ..services import UserService
from src.organizations.dependencies import OrganizationService, get_organization_service
from src.core.dependencies.email_deps import EmailService, get_email_service
from src.auth.dependencies.token_deps import TokenService, get_token_service
from src.authorization.dependencies import AuthorizationService, get_authorization_service
from .repositories import UserRepository, get_user_repository

def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> UserService:
    """Returns user service dependency"""
    return UserService(user_repo, email_service, token_service, organization_service, authorization_service)
