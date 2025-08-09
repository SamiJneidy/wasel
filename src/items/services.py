from src.core.config import settings
from .schemas import ItemOut, ItemCreate, ItemUpdate
from .repositories import ItemRepository
from .exceptions import ItemNotFoundException

class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo


    async def get(self, id: int) -> ItemOut:
        item = await self.item_repo.get(id)
        if not item:
            raise ItemNotFoundException()
        return ItemOut.model_validate(item)
    
    async def get_items_for_user(self) -> list[ItemOut]:
        query_set = await self.item_repo.get_items()
        result = [
            ItemOut.model_validate(item) for item in query_set
        ]
        return result
    
    async def create(self, data: ItemCreate) -> ItemOut:
        item = await self.item_repo.create(data.model_dump())
        return ItemOut.model_validate(item)
    
    async def update(self, id: int, data: ItemUpdate) -> ItemOut:
        item = await self.item_repo.update(id, data.model_dump())
        if not item:
            raise ItemNotFoundException()
        return ItemOut.model_validate(item)
    
    async def delete(self, id: int) -> None:
        item = await self.get(id)
        await self.item_repo.delete(id)
        return None
    