from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ..services import BranchService
from src.core.database import get_db
from src.tax_authorities.dependencies import get_tax_authority_service, TaxAuthorityService
from .repositories import BranchRepository, get_branch_repository

async def get_branch_service(
    branch_repo: Annotated[BranchRepository, Depends(get_branch_repository)],
    tax_authority_service: Annotated[TaxAuthorityService, Depends(get_tax_authority_service)],
) -> BranchService:
    return BranchService(branch_repo, tax_authority_service)
