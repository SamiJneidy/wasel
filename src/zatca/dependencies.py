from fastapi import Depends
from typing import Annotated
from .services import ZatcaService
from src.core.services import AsyncRequestService
from src.core.dependencies.requests_deps import get_requests_service
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import ZatcaRepository
from .services import ZatcaService
from src.branches.dependencies import BranchService, get_branch_service
from src.core.database import get_db

def get_zatca_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ZatcaRepository:
    return ZatcaRepository(db)


def get_zatca_service(
    repo: Annotated[ZatcaRepository, Depends(get_zatca_repository)],
    requests_service: Annotated[AsyncRequestService, Depends(get_requests_service)],
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
) -> ZatcaService:
    return ZatcaService(repo, requests_service, branch_service)
