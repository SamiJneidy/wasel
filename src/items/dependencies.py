from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from src.users.schemas import UserOut
from .repositories import ItemRepository
from .services import ItemService
from src.core.database import get_db
from src.auth.dependencies import get_current_user


def get_item_repository(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserOut, Depends(get_current_user)]
) -> ItemRepository:
    return ItemRepository(db, user)


def get_item_service(
    item_repo: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    
    return ItemService(item_repo)
