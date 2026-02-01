from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, update, delete, insert, func
from src.core.database import AsyncSession

from ..models import Permission, UserPermission, Role, RolePermission
from src.core.enums import UserStatus


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Application Permissions
    async def create_permissions(self, data: list[dict]) -> None:
        stmt = insert(Permission).values(data)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()

    async def get_permission_by_resource_action(self, resource: str, action: str) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.resource == resource, Permission.action == action)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_permissions(self) -> list[Permission]:
        stmt = select(Permission)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    # User Permissions
    async def get_user_permissions(self, organization_id: int, user_id: int) -> list[UserPermission]:
        stmt = (select(UserPermission).where(UserPermission.organization_id == organization_id, UserPermission.user_id == user_id))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_single_permission(self, organization_id: int, user_id: int, resource: str, action: str) -> UserPermission:
        stmt = (
            select(UserPermission)
            .join(Permission, UserPermission.permission_id == Permission.id)
            .where(
                UserPermission.organization_id == organization_id,
                UserPermission.user_id == user_id,
                Permission.resource == resource,
                Permission.action == action
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user_permissions(self, permissions: list[dict]) -> list[UserPermission]:
        stmt = insert(UserPermission).values(permissions).returning(UserPermission)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().all()
    
    async def delete_user_permissions(self, organization_id: int, user_id: int) -> None:
        stmt = delete(UserPermission).where(UserPermission.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
    
    # Role Permissions
    async def get_role(self, organization_id: int, role_id: int) -> Optional[Role]:
        stmt = select(Role).where(Role.organization_id == organization_id, Role.id == role_id, Role.is_immutable == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_roles(self, organization_id: int) -> list[Role]:
        stmt = select(Role).where(Role.organization_id == organization_id, Role.is_immutable == False)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_role_by_name(self, organization_id: int, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.organization_id == organization_id, Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def create_role(self, organization_id: int, data: Dict[str, Any]) -> Role:
        stmt = insert(Role).values(organization_id=organization_id, **data).returning(Role)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()
    
    async def update_role(self, organization_id: int, role_id: int, update_data: Dict[str, Any]) -> Optional[Role]:
        stmt = (
            update(Role)
            .where(Role.organization_id == organization_id, Role.id == role_id, Role.is_immutable == False)
            .values(update_data)
            .returning(Role)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()

    async def delete_role(self, organization_id: int, role_id: int) -> None:
        stmt = delete(Role).where(Role.organization_id == organization_id, Role.id == role_id, Role.is_immutable == False)
        await self.db.execute(stmt)
        await self.db.flush()
        return None

    async def get_role_permissions(self, organization_id: int, role_id: int) -> list[RolePermission]:
        stmt = (select(RolePermission).where(RolePermission.organization_id == organization_id, RolePermission.role_id == role_id))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_role_permissions(self, permissions: list[dict]) -> list[RolePermission]:
        stmt = insert(RolePermission).values(permissions).returning(RolePermission)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().all()
    
    async def delete_role_permissions(self, organization_id: int, role_id: int) -> None:
        stmt = delete(RolePermission).where(RolePermission.role_id == role_id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None