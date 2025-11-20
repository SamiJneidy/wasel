from src.core.config import settings
from src.users.schemas import UserOut
from .schemas import BranchOut, BranchCreate, BranchUpdate
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

    async def get(self, current_user: UserOut, id: int) -> Branch | None:
        return await self.repo.get(id)

    async def get_branches_for_organization(self, current_user: UserOut, organization_id: int) -> list[Branch]:
        return await self.repo.get_branches_for_organization(organization_id)

    async def create(self, current_user: UserOut, data: dict) -> Branch | None:
        return await self.repo.create(data)

    async def update(self, current_user: UserOut, id: int, data: dict) -> Branch | None:
        return await self.repo.update(id, data)

    async def delete(self, current_user: UserOut, id: int) -> None:
        return await self.repo.delete(id)
