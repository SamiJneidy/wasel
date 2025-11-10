from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from src.users.schemas import UserOut
from .repositories import BranchRepository
from .services import BranchService
from src.core.database import get_db
from src.users.dependencies import UserService, get_user_service
from src.core.dependencies import get_current_user


async def get_branch_repository(
    db: Annotated[Session, Depends(get_db)],
) -> BranchRepository:
    return BranchRepository(db)


async def get_branch_service(
    branch_repo: Annotated[BranchRepository, Depends(get_branch_repository)],
    user_email: Annotated[str, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> BranchService:
    user = await user_service.get_by_email(user_email)
    return BranchService(branch_repo)
