from src.core.config import settings
from src.branches.repositories import BranchRepository
from .schemas import OrganizationOut, OrganizationCreate, OrganizationUpdate, BranchCreate
from .repositories import OrganizationRepository
from .exceptions import OrganizationNotFoundException

class OrganizationService:
    def __init__(self, organization_repo: OrganizationRepository, branch_repo: BranchRepository):
        self.organization_repo = organization_repo
        self.branch_repo = branch_repo


    async def get_organization(self, id: int) -> OrganizationOut:
        organization = await self.organization_repo.get(id)
        if not organization:
            raise OrganizationNotFoundException()
        return OrganizationOut.model_validate(organization)
    
    async def create_organization(self, data: OrganizationCreate) -> OrganizationOut:
        organization = await self.organization_repo.create(data.model_dump())
        return OrganizationOut.model_validate(organization)
    
    async def create_organization_and_main_branch(self, data: OrganizationCreate) -> OrganizationOut:
        organization = await self.organization_repo.create(data.model_dump())
        branch = BranchCreate(**data.model_dump())
        branch_dict = branch.model_dump()
        branch_dict.update({"is_main_branch": True, "organization_id": organization.id})
        await self.branch_repo.create(branch_dict)
        return OrganizationOut.model_validate(organization)
    
    async def update_organization(self, id: int, data: OrganizationUpdate) -> OrganizationOut:
        organization = await self.organization_repo.update(id, data.model_dump())
        if not organization:
            raise OrganizationNotFoundException()
        return OrganizationOut.model_validate(organization)
    
    async def delete_organization(self, id: int) -> None:
        organization = await self.get_organization(id)
        await self.organization_repo.delete(id)
        return None
    