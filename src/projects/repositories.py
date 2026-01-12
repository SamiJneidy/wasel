from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, organization_id: int, branch_id: int, id: int) -> Optional[Project]:
        stmt = (
            select(Project)
            .where(Project.id == id, Project.organization_id == organization_id, Project.branch_id == branch_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_projects(
        self,
        organization_id: int,
        branch_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filters: Dict[str, Any] = {},
    ) -> Tuple[int, List[Project]]:
        stmt = select(Project).where(Project.organization_id == organization_id)
        count_stmt = (
            select(func.count())
            .select_from(Project)
            .where(Project.organization_id == organization_id, Project.branch_id == branch_id)
        )

        for k, v in filters.items():
            column = getattr(Project, k, None)
            if column is not None:
                if isinstance(v, str):
                    stmt = stmt.where(func.lower(column).like(f"%{v.lower()}%"))
                    count_stmt = count_stmt.where(func.lower(column).like(f"%{v.lower()}%"))
                else:
                    stmt = stmt.where(column == v)
                    count_stmt = count_stmt.where(column == v)

        # total count
        count_result = await self.db.execute(count_stmt)
        total_rows = count_result.scalars().first() or 0

        # pagination
        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        stmt = stmt.order_by(Project.created_at.desc())
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        return total_rows, projects

    async def create(self, organization_id: int, branch_id: int, user_id: int, data: Dict[str, Any]) -> Optional[Project]:
        item = Project(**data)
        item.organization_id = organization_id
        item.created_by = user_id
        item.branch_id = branch_id
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update(
        self,
        organization_id: int,
        branch_id: int,
        user_id: int,
        id: int,
        data: Dict[str, Any],
    ) -> Optional[Project]:
        stmt = (
            update(Project)
            .where(Project.id == id, Project.organization_id == organization_id, Project.branch_id == branch_id)
            .values(updated_by=user_id, **data)
            .returning(Project)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()

    async def delete(self, organization_id: int, branch_id: int, id: int) -> None:
        stmt = delete(Project).where(Project.id == id, Project.organization_id == organization_id, Project.branch_id == branch_id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
