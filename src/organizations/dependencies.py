from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from .repositories import OrganizationRepository
from .services import OrganizationService
from src.branches.dependencies import BranchRepository, get_branch_repository
from src.core.database import get_db


def get_organization_repository(
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationRepository:
    return OrganizationRepository(db)


def get_organization_service(
    organization_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    branch_repo: Annotated[BranchRepository, Depends(get_branch_repository)],
) -> OrganizationService:
    return OrganizationService(organization_repo, branch_repo)
