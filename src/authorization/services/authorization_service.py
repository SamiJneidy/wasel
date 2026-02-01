from src.core.schemas.context import RequestContext
from src.branches.schemas import BranchMinimal
from .permissions_service import PermissionService
from .user_branches_service import UserBranchService
from src.core.schemas.context import RequestContext
from src.branches.schemas import BranchMinimal
from ..exceptions import PermissionDeniedException
from ..schemas import (
    UserPermissionCreate,
    UserPermissionUpdate,
    UserPermissionOut
)
class AuthorizationService:
    def __init__(self, permission_service: PermissionService, user_branch_service: UserBranchService):
        self.permission_service = permission_service
        self.user_branch_service = user_branch_service

    # ---------------- Permissions ----------------

    async def get_permissions(self):
        return await self.permission_service.get_permissions()

    async def get_permissions_formatted(self):
        return await self.permission_service.get_permissions_formatted()

    async def get_user_permissions(self, ctx: RequestContext, user_id: int) -> UserPermissionOut:
        permissions = await self.permission_service.get_user_permissions(ctx.organization.id, user_id)
        allowed_branches = await self.user_branch_service.get_allowed_branches(ctx.organization.id, user_id)
        return UserPermissionOut(permissions=permissions, allowed_branches=allowed_branches)

    async def create_user_permissions(self, ctx: RequestContext, user_id: int, data: UserPermissionCreate) -> UserPermissionOut:
        permissions = await self.permission_service.create_user_permissions(ctx.organization.id, user_id, data)
        allowed_branches = await self.user_branch_service.grant_branches_to_user(ctx.organization.id, user_id, data.allowed_branch_ids)
        return UserPermissionOut(permissions=permissions, allowed_branches=allowed_branches)
    

    async def update_user_permissions(self, ctx: RequestContext, user_id: int, data: UserPermissionUpdate):
        permissions = await self.permission_service.update_user_permissions(ctx.organization.id, user_id, data)
        allowed_branches = await self.user_branch_service.update_allowed_branches(ctx.organization.id, user_id, data.allowed_branch_ids)
        return UserPermissionOut(permissions=permissions, allowed_branches=allowed_branches)

    async def delete_user_permissions(self, ctx: RequestContext, user_id: int):
        await self.permission_service.delete_user_permissions(ctx.organization.id, user_id)
        await self.user_branch_service.revoke_all_branches_from_user(ctx.organization.id, user_id)

    async def user_has_permission(self, ctx: RequestContext, user_id: int, resource: str, action: str) -> bool:
        return await self.permission_service.user_has_permission(ctx.organization.id, user_id, resource, action)

    async def create_user_permissions_after_signup(self, organization_id: int, user_id: int) -> None:
        await self.permission_service.create_user_permissions_after_signup(organization_id, user_id)

    # ---------------- Roles ----------------

    async def get_role(self, ctx: RequestContext, role_id: int):
        return await self.permission_service.get_role(ctx.organization.id, role_id)

    async def get_roles(self, ctx: RequestContext):
        return await self.permission_service.get_roles(ctx.organization.id)

    async def create_role(self, ctx: RequestContext, data):
        return await self.permission_service.create_role(ctx.organization.id, data)

    async def update_role(self, ctx: RequestContext, role_id: int, data):
        return await self.permission_service.update_role(ctx.organization.id, role_id, data)

    async def delete_role(self, ctx: RequestContext, role_id: int):
        await self.permission_service.delete_role(ctx.organization.id, role_id)

    async def create_default_roles(self, organization_id: int) -> int:
        return await self.permission_service.create_default_roles(organization_id)

    # ---------------- Branch access ----------------

    async def get_user_branches(self, ctx: RequestContext, user_id: int) -> list[BranchMinimal]:
        return await self.user_branch_service.get_allowed_branches(ctx.organization.id, user_id)

    async def grant_branches_to_user(self, ctx: RequestContext, user_id: int, branch_ids: list[int]):
        await self.user_branch_service.grant_branches_to_user(ctx.organization.id, user_id, branch_ids)

    async def update_allowed_branches(self, ctx: RequestContext, user_id: int, branch_ids: list[int]):
        await self.user_branch_service.update_allowed_branches(ctx.organization.id, user_id, branch_ids)

    async def user_has_branch_access(self, ctx: RequestContext, user_id: int, branch_id: int) -> bool:
        branches = await self.get_user_branches(ctx, user_id)
        return any(branch.id == branch_id for branch in branches)

    # ---------------- Final authorization ----------------

    async def authorize(self, ctx: RequestContext, user_id: int, branch_id: int, resource: str, action: str) -> None:
        if not await self.user_has_branch_access(ctx, user_id, branch_id):
            raise PermissionDeniedException(detail="User does not have access to this branch.")
        if not await self.user_has_permission(ctx, user_id, resource, action):
            raise PermissionDeniedException(detail=f"Missing permission: {resource}:{action}")

    async def is_allowed(self, ctx: RequestContext, user_id: int, branch_id: int, resource: str, action: str) -> bool:
        if not await self.user_has_branch_access(ctx, user_id, branch_id):
            return False
        return await self.user_has_permission(ctx, user_id, resource, action)
