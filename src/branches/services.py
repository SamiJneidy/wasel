from typing import List
from src.core.config import settings
from src.users.schemas import UserInDB
from .schemas import BranchOut, BranchCreate, BranchUpdate, BranchOutWithTaxAuthority
from .repositories import BranchRepository
from .exceptions import BranchNotFoundException
from src.core.enums import TaxAuthority, BranchStatus, BranchTaxIntegrationStatus
from src.tax_authorities.schemas import BranchTaxAuthorityDataCreate
from src.tax_authorities.services import TaxAuthorityService

class BranchService:
    def __init__(self, branch_repo: BranchRepository, tax_authority_service: TaxAuthorityService):
        self.branch_repo = branch_repo
        self.tax_authority_service = tax_authority_service

    async def get_branch(self, current_user: UserInDB, id: int) -> BranchOutWithTaxAuthority:
        db_branch = await self.branch_repo.get(id)
        if not db_branch:
            raise BranchNotFoundException()
        branch = BranchOutWithTaxAuthority.model_validate(db_branch)
        branch.tax_authority_data = await self.tax_authority_service.get_branch_tax_authority_data(current_user, branch.id, branch.tax_integration_status)
        return branch

    async def get_branches_for_organization(self, current_user: UserInDB) -> List[BranchOutWithTaxAuthority]:
        db_branches = await self.branch_repo.get_branches_for_organization(current_user.organization_id)
        branches = []
        for b in db_branches:
            branch = BranchOutWithTaxAuthority.model_validate(b)
            branch.tax_authority_data = await self.tax_authority_service.get_branch_tax_authority_data(current_user, b.id, b.tax_integration_status)
            branches.append(branch)
        return branches

    async def create_branch(self, current_user: UserInDB, data: BranchCreate, is_main_branch: bool = False) -> BranchOutWithTaxAuthority:
        data_dict = data.model_dump()
        status = BranchStatus.COMPLETED if current_user.organization.tax_authority is None else BranchStatus.PENDING
        data_dict.update({
            "organization_id": current_user.organization_id,
            "is_main_branch": is_main_branch,
            "tax_integration_status": BranchTaxIntegrationStatus.NOT_STARTED,
            "status": status
        })
        branch = await self.branch_repo.create(data_dict)
        return BranchOutWithTaxAuthority.model_validate(branch)

    async def create_branch_tax_authority_data(self, current_user: UserInDB, branch_id: int, data: BranchTaxAuthorityDataCreate) -> BranchOutWithTaxAuthority:
        branch = await self.get_branch(current_user, branch_id)
        await self.tax_authority_service.create_branch_tax_authority_data(current_user, branch_id, data)
        await self.branch_repo.update(branch_id, {
            "tax_integration_status": BranchTaxIntegrationStatus.PENDING_OTP,    
        })
        return await self.get_branch(current_user, branch_id)
    
    async def complete_branch_tax_authority_data(self, current_user: UserInDB, branch_id: int, data: BranchTaxAuthorityDataCreate) -> BranchOutWithTaxAuthority:
        branch = await self.get_branch(current_user, branch_id)
        await self.tax_authority_service.complete_branch_tax_authority_data(current_user, branch_id, data)
        await self.branch_repo.update(branch_id, {
            "tax_integration_status": BranchTaxIntegrationStatus.COMPLETED,
            "status": BranchStatus.COMPLETED,    
        })
        return await self.get_branch(current_user, branch_id)
    
    async def update_branch(self, current_user: UserInDB, id: int, data: BranchUpdate) -> BranchOutWithTaxAuthority:
        branch = await self.branch_repo.update(id, data.model_dump())
        if not branch:
            raise BranchNotFoundException()
        # if branch.organization_id != current_user.organization_id:
        #     raise BranchNotFoundException()
        return BranchOutWithTaxAuthority.model_validate(branch)

    async def update_branch_status(self, current_user: UserInDB, id: int, status: BranchStatus) -> BranchOutWithTaxAuthority:
        branch = await self.branch_repo.update(id, {"status": status})
        if not branch:
            raise BranchNotFoundException()
        return BranchOutWithTaxAuthority.model_validate(branch)

    async def delete_branch(self, current_user: UserInDB, id: int) -> None:
        _ = await self.get_branch(current_user, id)
        await self.branch_repo.delete(id)
        return None
