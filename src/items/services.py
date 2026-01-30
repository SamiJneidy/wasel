from .schemas import ItemOut, ItemCreate, ItemUpdate, ItemFilters
from src.core.schemas import PagintationParams
from .repositories import ItemRepository
from .exceptions import ItemNotFoundException
from src.core.schemas.context import RequestContext

class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    async def get_item(self, ctx: RequestContext, id: int) -> ItemOut:
        item = await self.item_repo.get_item(ctx.organization.id, id)
        if not item:
            raise ItemNotFoundException()
        return ItemOut.model_validate(item)

    async def get_items(self, ctx: RequestContext, pagination_params: PagintationParams, filters: ItemFilters) -> tuple[int, list[ItemOut]]:
        total, query_set = await self.item_repo.get_items(
            ctx.organization.id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [ItemOut.model_validate(item) for item in query_set]

    async def create_item(self, ctx: RequestContext, data: ItemCreate) -> ItemOut:
        item = await self.item_repo.create_item(ctx.organization.id, ctx.user.id, data.model_dump())
        return ItemOut.model_validate(item)

    async def update_item(self, ctx: RequestContext, id: int, data: ItemUpdate) -> ItemOut:
        item = await self.item_repo.update_item(ctx.organization.id, ctx.user.id, id, data.model_dump(exclude_unset=True))
        if not item:
            raise ItemNotFoundException()
        return ItemOut.model_validate(item)

    async def delete_item(self, ctx: RequestContext, id: int) -> None:
        await self.get_item(ctx, id)
        await self.item_repo.delete_item(ctx.organization.id, id)
        return None
