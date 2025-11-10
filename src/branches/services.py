from src.core.config import settings
from .schemas import BranchOut, BranchCreate, BranchUpdate, UserOut
from .repositories import BranchRepository
from .exceptions import BranchNotFoundException

class BranchService:
    def __init__(self, branch_repo: BranchRepository, user: UserOut):
        self.user = user
        self.branch_repo = branch_repo


    async def get_branch(self, id: int) -> BranchOut:
        branch = await self.branch_repo.get(id)
        if not branch:
            raise BranchNotFoundException()
        return BranchOut.model_validate(branch)
    
    async def get_branches_for_organization(self) -> BranchOut:
        branches = await self.branch_repo.get_branches_for_organization(self.user.organization_id)
        return [BranchOut.model_validate(branch) for branch in branches]
    
    async def create_branch(self, data: BranchCreate, is_main_branch: bool = False) -> BranchOut:
        data_dict = data.model_dump()
        data_dict.update({"organization_id": self.user.organization_id, "is_main_branch": is_main_branch})
        branch = await self.branch_repo.create(data_dict)
        return BranchOut.model_validate(branch)
    
    async def update_branch(self, id: int, data: BranchUpdate) -> BranchOut:
        branch = await self.branch_repo.update(id, data.model_dump())
        if not branch:
            raise BranchNotFoundException()
        return BranchOut.model_validate(branch)
    
    async def delete_branch(self, id: int) -> None:
        branch = await self.get_branch(id)
        await self.branch_repo.delete(id)
        return None
    