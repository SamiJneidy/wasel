from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ..repositories import TokenRepository
from ..services import TokenService
from src.core.database import get_db

def get_token_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> TokenRepository:
    """Returns otp repository dependency"""
    return TokenRepository(db)


def get_token_service(
    token_repo: Annotated[TokenRepository, Depends(get_token_repository)],
) -> TokenService:
    """Returns otp service dependency"""
    return TokenService(token_repo)
