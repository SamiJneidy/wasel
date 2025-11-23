from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Item


class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, organization_id: int, id: int) -> Optional[Item]:
        stmt = (
            select(Item)
            .where(Item.id == id, Item.organization_id == organization_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_items(
        self,
        organization_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filters: Dict[str, Any] = {},
    ) -> Tuple[int, List[Item]]:
        stmt = select(Item).where(Item.organization_id == organization_id)
        count_stmt = (
            select(func.count())
            .select_from(Item)
            .where(Item.organization_id == organization_id)
        )

        for k, v in filters.items():
            column = getattr(Item, k, None)
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

        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return total_rows, items

    async def create(self, organization_id: int, user_id: int, data: Dict[str, Any]) -> Optional[Item]:
        item = Item(**data)
        item.organization_id = organization_id
        item.created_by = user_id
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update(
        self,
        organization_id: int,
        user_id: int,
        id: int,
        data: Dict[str, Any],
    ) -> Optional[Item]:
        stmt = (
            update(Item)
            .where(Item.id == id, Item.organization_id == organization_id)
            .values(updated_by=user_id, **data)
            .returning(Item)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()

    async def delete(self, organization_id: int, id: int) -> None:
        stmt = delete(Item).where(Item.id == id, Item.organization_id == organization_id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
