from sqlalchemy import select, update, delete, insert, or_, func
from src.core.database import AsyncSession

from ..models import UserBranch

class UserBranchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_allowed_branches(self, organization_id: int, user_id: int) -> list[UserBranch]:
        stmt = (
            select(UserBranch)
            .where(
                UserBranch.organization_id == organization_id, 
                UserBranch.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def grant_branch_to_user(self, organization_id: int, branch_id: int, user_id: int) -> None:
        stmt = (
            insert(UserBranch)
            .values(organization_id=organization_id, branch_id=branch_id, user_id=user_id)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    
    async def grant_branches_to_user(self, data: list[dict]) -> None:
        stmt = insert(UserBranch)
        await self.db.execute(stmt, data)
        await self.db.flush()

    async def revoke_all_branches_from_user(self, organization_id: int, user_id: int) -> None:
        stmt = (
            delete(UserBranch)
            .where(UserBranch.organization_id == organization_id, UserBranch.user_id == user_id)
        )
        await self.db.execute(stmt)
        await self.db.flush()