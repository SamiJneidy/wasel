from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import OrganizationRepository
from .services import OrganizationService
from src.core.database import get_db


def get_organization_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationRepository:
    return OrganizationRepository(db)


def get_organization_service(
    organization_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
) -> OrganizationService:
    return OrganizationService(organization_repo)
