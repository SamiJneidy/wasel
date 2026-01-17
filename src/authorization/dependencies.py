from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import AuthorizationRepository
from .services import AuthorizationService
from src.core.database import get_db
from .exceptions import PermissionDeniedException

def get_authorization_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthorizationRepository:
    """Returns authorization repository dependency."""
    return AuthorizationRepository(db)

def get_authorization_service(
    authorization_repo: Annotated[AuthorizationRepository, Depends(get_authorization_repository)],
) -> AuthorizationService:
    """Returns authorization service dependency"""
    return AuthorizationService(authorization_repo)
