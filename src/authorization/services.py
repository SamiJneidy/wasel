from sqlalchemy.exc import IntegrityError
from src.users.schemas import UserInDB
from .repositories import AuthorizationRepository
from .schemas import (
    RolePermissionCreateInternal,
    UserPermissionCreate,
    UserPermissionCreateInternal,
    UserPermissionUpdate,
    UserPermissionOut,
    PermissionOut,
    RoleCreate,
    RoleUpdate,
    RoleWithPermissionsOut,
)
from .exceptions import (
    InvalidPermissionException,
    RoleCannotBeDeletedException,
    RoleNotFoundException,
    RoleImmutableException
)
from .default_roles import DEFAULT_ROLES

class AuthorizationService:
    def __init__(
        self,
        permission_repo: AuthorizationRepository,
    ):
        self.authorization_repo = permission_repo
    
    async def _validate_permissions(self, permissions: list[str]) -> None:
        for perm in permissions:
            resource, action = perm.split(":")
            permission = await self.authorization_repo.get_permission_by_resource_action(resource, action)
            if not permission:
                raise InvalidPermissionException(f"Permission {perm} does not exist.")

    async def _validate_immutable_role(self, organization_id: int, role_id: int) -> None:
        role = await self.authorization_repo.get_role(organization_id, role_id)
        if not role:
            raise RoleNotFoundException()
        if role.is_immutable:
            raise RoleImmutableException()
        
    async def get_user_permissions(self, user: UserInDB, user_id: int) -> list[str]:
        permissions = await self.authorization_repo.get_user_permissions(user.organization_id, user_id)
        return [f"{perm.permission.resource}:{perm.permission.action}" for perm in permissions if perm.is_allowed]
    
    async def get_permissions(self) -> list[PermissionOut]:
        permissions = await self.authorization_repo.get_permissions()
        return [PermissionOut.model_validate(perm) for perm in permissions]

    async def user_has_permission(self, organization_id: int, user_id: int, resource: str, action: str) -> bool:
        permission = await self.authorization_repo.get_single_permission(organization_id, user_id, resource, action)
        if permission is None or permission.is_allowed == False:
            return False
        return True

    async def create_user_permissions(self, user: UserInDB, user_id: int, data: UserPermissionCreate) -> UserPermissionOut:
        permissions = await self.authorization_repo.get_permissions()
        await self._validate_permissions(data.permissions)
        # Create permissions
        user_permissions: list[dict] = []
        for perm in permissions:
            is_allowed = perm.resource + ":" + perm.action in data.permissions
            permission = UserPermissionCreateInternal(
                user_id=user_id,
                organization_id=user.organization_id,
                permission_id=perm.id,
                is_allowed=is_allowed,
            )
            user_permissions.append(permission.model_dump())
        await self.authorization_repo.create_user_permissions(user_permissions)
        return await self.get_user_permissions(user, user_id)
    
    async def create_user_permissions_after_signup(self, organization_id: int, user_id: int) -> None:
        permissions = await self.authorization_repo.get_permissions()
        # Create permissions
        user_permissions: list[dict] = []
        for perm in permissions:
            permission = UserPermissionCreateInternal(
                user_id=user_id,
                organization_id=organization_id,
                permission_id=perm.id,
                is_allowed=True,
            )
            user_permissions.append(permission.model_dump())
        await self.authorization_repo.create_user_permissions(user_permissions)

    async def update_user_permissions(self, user: UserInDB, user_id: int, data: UserPermissionUpdate) -> UserPermissionOut:
        await self.authorization_repo.delete_user_permissions(user.organization_id, user_id)
        return await self.create_user_permissions(user, user_id, data)
    
    async def delete_user_permissions(self, user: UserInDB, user_id: int) -> None:
        await self.authorization_repo.delete_user_permissions(user.organization_id, user_id)

    async def get_role(self, user: UserInDB, role_id: int) -> RoleWithPermissionsOut:
        role = await self.authorization_repo.get_role(user.organization_id, role_id)
        if not role:
            raise RoleNotFoundException()
        permissions = await self.authorization_repo.get_role_permissions(user.organization_id, role_id)
        allowed_permissions = [f"{perm.permission.resource}:{perm.permission.action}" for perm in permissions if perm.is_allowed]
        return RoleWithPermissionsOut(
            id=role.id, 
            name=role.name, 
            description=role.description, 
            permissions=allowed_permissions,
        )

    async def get_roles(self, user: UserInDB) -> list[RoleWithPermissionsOut]:
        roles = await self.authorization_repo.get_roles(user.organization_id)
        roles_list: list[RoleWithPermissionsOut] = []
        for role in roles:
            permissions = await self.authorization_repo.get_role_permissions(user.organization_id, role.id)
            allowed_permissions = [f"{perm.permission.resource}:{perm.permission.action}" for perm in permissions if perm.is_allowed]
            roles_list.append(
                RoleWithPermissionsOut(
                    id=role.id, 
                    name=role.name, 
                    description=role.description, 
                    permissions=allowed_permissions,
                )
            )
        return roles_list

    async def create_role(self, user: UserInDB, data: RoleCreate) -> RoleWithPermissionsOut:
        role_data = {
            "name": data.name,
            "description": data.description,
            "is_immutable": False,
        }
        role = await self.authorization_repo.create_role(user.organization_id, role_data)
        await self._create_role_permissions(user.organization_id, role.id, data.permissions)
        return await self.get_role(user, role.id)

    async def create_default_roles(self, organization_id: int) -> int:
        """Created default roles for a new organization and returns the id of the SUPER_ADMIN role."""
        super_admin_role_id = None
        permissions = await self.authorization_repo.get_permissions()
        for role, data in DEFAULT_ROLES.items():
            role_permissions = data.pop("permissions")
            role_data = data
            role = await self.authorization_repo.create_role(organization_id, role_data)
            if role_data["name"] == "SUPER_ADMIN":
                super_admin_role_id = role.id
            permissions_list: list[dict] = []
            for perm in permissions:
                is_allowed = perm.resource + ":" + perm.action in role_permissions
                permission = RolePermissionCreateInternal(
                    role_id=role.id,
                    organization_id=organization_id,
                    permission_id=perm.id,
                    is_allowed=is_allowed,
                )
                permissions_list.append(permission.model_dump())
            await self.authorization_repo.create_role_permissions(permissions_list)
        return super_admin_role_id
    
    async def _create_role_permissions(self, organization_id: int, role_id: int, permissions_list: list[str]) -> None:
        permissions = await self.authorization_repo.get_permissions()
        await self._validate_permissions(permissions_list)
        # Create permissions
        role_permissions: list[dict] = []
        for perm in permissions:
            is_allowed = perm.resource + ":" + perm.action in permissions_list
            permission = RolePermissionCreateInternal(
                role_id=role_id,
                organization_id=organization_id,
                permission_id=perm.id,
                is_allowed=is_allowed,
            )
            role_permissions.append(permission.model_dump())
        await self.authorization_repo.create_role_permissions(role_permissions)

    async def update_role(self, user: UserInDB, role_id: int, data: RoleUpdate) -> RoleWithPermissionsOut:
        await self._validate_immutable_role(user.organization_id, role_id)
        role_data = data.model_dump(exclude={"permissions"}, exclude_none=True)
        await self.authorization_repo.update_role(user.organization_id, role_id, role_data)
        await self.authorization_repo.delete_role_permissions(user.organization_id, role_id)
        await self._create_role_permissions(user.organization_id, role_id, data.permissions)
        return await self.get_role(user, role_id)
    
    async def delete_role(self, user: UserInDB, role_id: int) -> None:
        await self._validate_immutable_role(user.organization_id, role_id)
        try:
            await self.authorization_repo.delete_role_permissions(user.organization_id, role_id)
            await self.authorization_repo.delete_role(user.organization_id, role_id)
        except IntegrityError as e:
            raise RoleCannotBeDeletedException(detail="Role cannot be deleted because it is assigned to one or more users.")
