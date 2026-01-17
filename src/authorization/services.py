from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from src.organizations.exceptions import OrganizationNotFoundException
from src.users.schemas import UserInDB
from .repositories import AuthorizationRepository
from .schemas import (
    UserPermissionCreate,
    UserPermissionCreateInternal,
    UserPermissionUpdate,
    UserPermissionOut,
    PermissionOut,
    
)
from src.auth.schemas.token_schemas import UserInviteToken
from .exceptions import (
    InvalidPermissionException
)
from src.core.schemas import PagintationParams
from src.organizations.services import OrganizationService
from src.auth.services.token_service import TokenService
from src.core.services import EmailService
from src.core.config import settings
from src.core.enums import UserStatus, UserType


class AuthorizationService:
    def __init__(
        self,
        permission_repo: AuthorizationRepository,
    ):
        self.permission_repo = permission_repo
        
    async def get_user_permissions(self, user: UserInDB, user_id: int) -> list[str]:
        permissions = await self.permission_repo.get_user_permissions(user.organization_id, user_id)
        return [f"{perm.permission.resource}:{perm.permission.action}" for perm in permissions if perm.is_allowed]
    
    async def get_permissions(self) -> list[PermissionOut]:
        permissions = await self.permission_repo.get_permissions()
        return [PermissionOut.model_validate(perm) for perm in permissions]

    async def user_has_permission(self, organization_id: int, user_id: int, resource: str, action: str) -> bool:
        permission = await self.permission_repo.get_single_permission(organization_id, user_id, resource, action)
        if permission is None or permission.is_allowed == False:
            return False
        return True

    async def create_user_permissions(self, user: UserInDB, user_id: int, data: UserPermissionCreate) -> UserPermissionOut:
        permissions = await self.permission_repo.get_permissions()
        # Validate permissions
        for perm in data.permissions:
            resource, action = perm.split(":")
            permission = await self.permission_repo.get_permission_by_resource_action(resource, action)
            if not permission:
                raise InvalidPermissionException(f"Permission {perm} does not exist.")
            
        # Create permissions
        user_permissions: list[dict] = []
        for perm in permissions:
            is_allowed = perm.resource + ":" + perm.action in data.permissions
            permission = UserPermissionCreateInternal(
                user_id=user_id,
                organization_id=user.organization_id,
                permission_id=perm.id,
                is_allowed=is_allowed,
            )
            user_permissions.append(permission.model_dump())
        await self.permission_repo.create_user_permissions(user_permissions)
        return await self.get_user_permissions(user, user_id)
    
    async def create_user_permissions_after_signup(self, organization_id: int, user_id: int) -> None:
        permissions = await self.permission_repo.get_permissions()
        # Create permissions
        user_permissions: list[dict] = []
        for perm in permissions:
            permission = UserPermissionCreateInternal(
                user_id=user_id,
                organization_id=organization_id,
                permission_id=perm.id,
                is_allowed=True,
            )
            user_permissions.append(permission.model_dump())
        await self.permission_repo.create_user_permissions(user_permissions)

    async def update_user_permissions(self, user: UserInDB, user_id: int, data: UserPermissionUpdate) -> UserPermissionOut:
        await self.permission_repo.delete_user_permissions(user.organization_id, user_id)
        return await self.create_user_permissions(user, user_id, data)
    
    async def delete_user_permissions(self, user: UserInDB, user_id: int) -> None:
        await self.permission_repo.delete_user_permissions(user.organization_id, user_id)