from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from src.users.schemas import UserOut
from .repositories import ItemRepository
from .services import ItemService
from src.core.database import get_db
from src.users.dependencies import UserService, get_user_service
from src.core.dependencies import get_current_user


async def get_item_repository(
    db: Annotated[Session, Depends(get_db)],
    user_email: Annotated[str, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ItemRepository:
    user = await user_service.get_by_email(user_email)
    return ItemRepository(db, user)


def get_item_service(
    item_repo: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    
    return ItemService(item_repo)
