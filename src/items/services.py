from src.users.schemas import UserInDB

from .schemas import (
    ItemOut,
    ItemCreate,
    ItemUpdate,
    ItemFilters,
)
from src.core.schemas import PagintationParams
from .repositories import ItemRepository
from .exceptions import ItemNotFoundException


class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    async def get(self, user: UserInDB, id: int) -> ItemOut:
        item = await self.item_repo.get(user.organization_id, id)
        if not item:
            raise ItemNotFoundException()
        return ItemOut.model_validate(item)

    async def get_items(
        self,
        user: UserInDB,
        pagination_params: PagintationParams,
        filters: ItemFilters,
    ) -> tuple[int, list[ItemOut]]:
        total, query_set = await self.item_repo.get_items(
            user.organization_id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [ItemOut.model_validate(item) for item in query_set]

    async def create(self, user: UserInDB, data: ItemCreate) -> ItemOut:
        item = await self.item_repo.create(
            user.organization_id,
            user.id,
            data.model_dump(),
        )
        return ItemOut.model_validate(item)

    async def update(
        self,
        user: UserInDB,
        id: int,
        data: ItemUpdate,
    ) -> ItemOut:
        item = await self.item_repo.update(
            user.organization_id,
            user.id,
            id,
            data.model_dump(exclude_unset=True),
        )
        if not item:
            raise ItemNotFoundException()
        return ItemOut.model_validate(item)

    async def delete(self, user: UserInDB, id: int) -> None:
        await self.get(user, id)
        await self.item_repo.delete(user.organization_id, id)
        return None
