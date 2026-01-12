from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import ProjectRepository
from .services import ProjectService
from src.core.database import get_db


async def get_project_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectRepository:
    return ProjectRepository(db)


def get_project_service(
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> ProjectService:
    
    return ProjectService(project_repo)
