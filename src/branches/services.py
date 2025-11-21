from typing import List
from src.core.config import settings
from src.users.schemas import UserInDB
from .schemas import BranchOut, BranchCreate, BranchUpdate
from .repositories import BranchRepository
from .exceptions import BranchNotFoundException


class BranchService:
    def __init__(self, branch_repo: BranchRepository):
        self.branch_repo = branch_repo

    async def get_branch(self, current_user: UserInDB, id: int) -> BranchOut:
        branch = await self.branch_repo.get(id)
        if not branch:
            raise BranchNotFoundException()
        
        # if branch.organization_id != current_user.organization_id:
        #     raise BranchNotFoundException()

        return BranchOut.model_validate(branch)

    async def get_branches_for_organization(self, current_user: UserInDB) -> List[BranchOut]:
        branches = await self.branch_repo.get_branches_for_organization(current_user.organization_id)
        return [BranchOut.model_validate(branch) for branch in branches]

    async def create_branch(self, current_user: UserInDB, data: BranchCreate, is_main_branch: bool = False) -> BranchOut:
        data_dict = data.model_dump()
        data_dict.update({
            "organization_id": current_user.organization_id,
            "is_main_branch": is_main_branch,
        })
        branch = await self.branch_repo.create(data_dict)
        return BranchOut.model_validate(branch)

    async def update_branch(self, current_user: UserInDB, id: int, data: BranchUpdate) -> BranchOut:
        branch = await self.branch_repo.update(id, data.model_dump())
        if not branch:
            raise BranchNotFoundException()
        # if branch.organization_id != current_user.organization_id:
        #     raise BranchNotFoundException()
        return BranchOut.model_validate(branch)

    async def delete_branch(self, current_user: UserInDB, id: int) -> None:
        _ = await self.get_branch(current_user, id)
        await self.branch_repo.delete(id)
        return None
