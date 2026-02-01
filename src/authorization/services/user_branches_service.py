from ..repositories.user_branches_repo import UserBranchRepository
from ..exceptions import (
    InvalidBranchesException
)
from src.users.repositories import UserRepository
from src.branches.schemas import BranchMinimal
from src.branches.repositories import BranchRepository

class UserBranchService:
    def __init__(
        self,
        user_branch_repo: UserBranchRepository,
        user_repo: UserRepository,
        branch_repo: BranchRepository
    ):  
        self.user_branch_repo = user_branch_repo
        self.user_repo = user_repo
        self.branch_repo = branch_repo

    async def get_allowed_branches(self, organization_id: int, user_id: int) -> list[BranchMinimal]:
        user = await self.user_repo.get(user_id)
        if not user:
            return []
        
        if user.is_super_admin:
            all_branches = await self.branch_repo.get_branches(organization_id)
            return [BranchMinimal.model_validate(branch) for branch in all_branches]
        
        user_branches = await self.user_branch_repo.get_allowed_branches(organization_id, user_id)
        allowed_branches = [BranchMinimal.model_validate(b.branch) for b in user_branches]
        
        allowed_branches_ids = {b.id for b in allowed_branches}
        if user.default_branch_id not in allowed_branches_ids:
            default_branch = await self.branch_repo.get_branch(user.default_branch_id)
            allowed_branches.append(BranchMinimal.model_validate(default_branch))

        return allowed_branches

    async def grant_branch_to_user(self, organization_id: int, user_id: int, branch_id: int) -> None:
        await self.user_branch_repo.grant_branch_to_user(organization_id, branch_id, user_id)

    async def grant_branches_to_user(self, organization_id: int, user_id: int, allowed_branch_ids: list[int]) -> None:
        # Validate branches
        branches_ids_set = set(allowed_branch_ids)
        all_branches = await self.branch_repo.get_branches(organization_id)
        all_branches_ids_set = {int(branch.id) for branch in all_branches}
        if not branches_ids_set.issubset(all_branches_ids_set):
            raise InvalidBranchesException()
        
        data: list[dict] = []
        for branch_id in allowed_branch_ids:
            data.append({
                "organization_id": organization_id,
                "user_id": user_id,
                "branch_id": branch_id
            })
        await self.user_branch_repo.grant_branches_to_user(data)

    
    async def revoke_all_branches_from_user(self, organization_id: int, user_id: int) -> None:
        await self.user_branch_repo.revoke_all_branches_from_user(organization_id, user_id)

    async def update_allowed_branches(self, organization_id: int, user_id: int, allowed_branch_ids: list[int]) -> None:
        await self.revoke_all_branches_from_user(organization_id, user_id)
        await self.grant_branches_to_user(organization_id, user_id, allowed_branch_ids)
