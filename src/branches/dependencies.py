from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import BranchRepository
from .services import BranchService
from src.core.database import get_db


async def get_branch_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BranchRepository:
    return BranchRepository(db)


async def get_branch_service(
    branch_repo: Annotated[BranchRepository, Depends(get_branch_repository)],
) -> BranchService:
    return BranchService(branch_repo)
