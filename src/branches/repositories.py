from typing import Optional, Dict, Any

from sqlalchemy import select, update, delete
from src.core.database import AsyncSession

from .models import Branch


class BranchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_branch(self, organization_id: int, id: int) -> Optional[Branch]:
        stmt = select(Branch).where(Branch.id == id, Branch.organization_id == organization_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_branches(self, organization_id: int) -> list[Branch]:
        stmt = select(Branch).where(Branch.organization_id == organization_id).order_by(Branch.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_branch(self, data: Dict[str, Any]) -> Branch:
        branch = Branch(**data)
        self.db.add(branch)
        await self.db.flush()
        await self.db.refresh(branch)
        return branch

    async def update_branch(self, id: int, data: Dict[str, Any]) -> Optional[Branch]:
        stmt = (
            update(Branch)
            .where(Branch.id == id)
            .values(**data)
            .returning(Branch)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def delete_branch(self, id: int) -> None:
        stmt = delete(Branch).where(Branch.id == id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
