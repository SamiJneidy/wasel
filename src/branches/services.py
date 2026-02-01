from typing import List
from src.core.schemas.context import RequestContext
from .schemas import BranchOut, BranchCreate, BranchUpdate, BranchOutWithTaxAuthority
from .repositories import BranchRepository
from .exceptions import BranchNotFoundException
from src.core.enums import TaxAuthority, BranchStatus, BranchTaxIntegrationStatus
from src.tax_authorities.schemas import BranchTaxAuthorityDataCreate, BranchTaxAuthorityDataUpdate
from src.tax_authorities.services import TaxAuthorityService

class BranchService:
    def __init__(self, branch_repo: BranchRepository, tax_authority_service: TaxAuthorityService):
        self.branch_repo = branch_repo
        self.tax_authority_service = tax_authority_service

    async def get_branch(self, ctx: RequestContext, id: int) -> BranchOutWithTaxAuthority:
        db_branch = await self.branch_repo.get_branch(ctx.organization.id, id)
        if not db_branch:
            raise BranchNotFoundException()
        branch = BranchOutWithTaxAuthority.model_validate(db_branch)
        branch.tax_authority_data = await self.tax_authority_service.get_branch_tax_authority_data(ctx, branch.id, branch.tax_integration_status)
        return branch

    async def get_branches(self, ctx: RequestContext) -> List[BranchOutWithTaxAuthority]:
        db_branches = await self.branch_repo.get_branches(ctx.organization.id)
        branches = []
        for b in db_branches:
            branch = BranchOutWithTaxAuthority.model_validate(b)
            branch.tax_authority_data = await self.tax_authority_service.get_branch_tax_authority_data(ctx, b.id, b.tax_integration_status)
            branches.append(branch)
        return branches

    async def create_branch(self, ctx: RequestContext, data: BranchCreate, is_main_branch: bool = False) -> BranchOutWithTaxAuthority:
        data_dict = data.model_dump()
        status = BranchStatus.COMPLETED if ctx.organization.tax_authority is None else BranchStatus.PENDING
        data_dict.update({
            "organization_id": ctx.organization.id,
            "is_main_branch": is_main_branch,
            "tax_integration_status": BranchTaxIntegrationStatus.NOT_STARTED,
            "status": status
        })
        branch = await self.branch_repo.create_branch(data_dict)
        return BranchOutWithTaxAuthority.model_validate(branch)

    async def create_branch_tax_authority_data(self, ctx: RequestContext, data: BranchTaxAuthorityDataCreate) -> BranchOutWithTaxAuthority:
        await self.tax_authority_service.create_branch_tax_authority_data(ctx, ctx.branch.id, data)
        await self.branch_repo.update_branch(ctx.branch.id, {"tax_integration_status": BranchTaxIntegrationStatus.PENDING_OTP})
        return await self.get_branch(ctx, ctx.branch.id)
    
    async def update_branch_tax_authority_data(self, ctx: RequestContext, data: BranchTaxAuthorityDataUpdate) -> BranchOutWithTaxAuthority:
        await self.tax_authority_service.update_branch_tax_authority_data(ctx, ctx.branch.id, data)
        return await self.get_branch(ctx, ctx.branch.id)
    
    async def complete_branch_tax_authority_data(self, ctx: RequestContext, data: BranchTaxAuthorityDataCreate) -> BranchOutWithTaxAuthority:
        branch = await self.get_branch(ctx, ctx.branch.id)
        await self.tax_authority_service.complete_branch_tax_authority_data(ctx, ctx.branch.id, data)
        await self.branch_repo.update_branch(ctx.branch.id, {
            "tax_integration_status": BranchTaxIntegrationStatus.COMPLETED,
            "status": BranchStatus.COMPLETED,    
        })
        return await self.get_branch(ctx, ctx.branch.id)
    
    async def update_branch(self, ctx: RequestContext, id: int, data: BranchUpdate) -> BranchOutWithTaxAuthority:
        branch = await self.branch_repo.update_branch(id, data.model_dump())
        if not branch:
            raise BranchNotFoundException()
        # if branch.organization_id != ctx.organization_id:
        #     raise BranchNotFoundException()
        return BranchOutWithTaxAuthority.model_validate(branch)

    async def update_branch_status(self, ctx: RequestContext, id: int, status: BranchStatus) -> BranchOutWithTaxAuthority:
        branch = await self.branch_repo.update_branch(id, {"status": status})
        if not branch:
            raise BranchNotFoundException()
        return BranchOutWithTaxAuthority.model_validate(branch)

    async def delete_branch(self, ctx: RequestContext, id: int) -> None:
        _ = await self.get_branch(ctx, id)
        await self.branch_repo.delete_branch(id)
        return None
