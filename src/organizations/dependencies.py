from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from src.users.schemas import UserOut
from .repositories import OrganizationRepository
from .services import OrganizationService
from src.core.database import get_db
from src.auth.dependencies import get_current_user


def get_organization_repository(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserOut, Depends(get_current_user)]
) -> OrganizationRepository:
    return OrganizationRepository(db, user)


def get_organization_service(
    organization_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
) -> OrganizationService:
    
    return OrganizationService(organization_repo)
