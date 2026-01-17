from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, update, delete, insert, func
from src.core.database import AsyncSession

from .models import Permission, UserPermission
from src.core.enums import UserStatus


class AuthorizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

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