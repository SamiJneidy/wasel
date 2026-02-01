from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from src.users.dependencies.repositories import UserRepository, get_user_repository
from src.branches.dependencies.repositories import BranchRepository, get_branch_repository
from .repositories.permissions_repo import PermissionRepository
from .repositories.user_branches_repo import UserBranchRepository
from .services.permissions_service import PermissionService
from .services.user_branches_service import UserBranchService
from .services.authorization_service import AuthorizationService
from src.core.database import get_db

def get_permissions_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> PermissionRepository:
    """Returns permissions repository dependency."""
    return PermissionRepository(db)

def get_user_branches_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserBranchRepository:
    """Returns user branches repository dependency."""
    return UserBranchRepository(db)

def get_permissions_service(
    permissions_repo: Annotated[PermissionRepository, Depends(get_permissions_repository)],
) -> PermissionService:
    """Returns permissions service dependency"""
    return PermissionService(permissions_repo)

def get_user_branches_service(
    user_branches_repo: Annotated[UserBranchRepository, Depends(get_permissions_repository)],
    user_repo: UserRepository = Depends(get_user_repository),
    branch_repo: BranchRepository = Depends(get_branch_repository)
) -> UserBranchService:
    """Returns user branches service dependency"""
    return UserBranchService(user_branches_repo, user_repo, branch_repo)

def get_authorization_service(
    permissions_service: PermissionService = Depends(get_permissions_service),
    user_branches_service: UserBranchService = Depends(get_user_branches_service),
) -> AuthorizationService:
    """Returns authorization service dependency"""
    return AuthorizationService(permissions_service, user_branches_service)
