from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import ItemRepository
from .services import ItemService
from src.core.database import get_db


async def get_item_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemRepository:
    return ItemRepository(db)


def get_item_service(
    item_repo: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    
    return ItemService(item_repo)
