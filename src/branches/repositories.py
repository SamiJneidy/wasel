from typing import Optional, Dict, Any

from sqlalchemy import select, update, delete
from src.core.database import AsyncSession

from .models import Branch


class BranchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Branch]:
        stmt = select(Branch).where(Branch.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_branches_for_organization(self, organization_id: int) -> list[Branch]:
        stmt = select(Branch).where(Branch.organization_id == organization_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, data: Dict[str, Any]) -> Branch:
        branch = Branch(**data)
        self.db.add(branch)
        await self.db.flush()
        await self.db.refresh(branch)
        return branch

    async def update(self, id: int, data: Dict[str, Any]) -> Optional[Branch]:
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

    async def delete(self, id: int) -> None:
        stmt = delete(Branch).where(Branch.id == id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
