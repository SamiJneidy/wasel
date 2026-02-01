from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ..repositories import UserRepository
from src.core.database import get_db
def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    """Returns user repository dependency."""
    return UserRepository(db)
