from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin
from src.organizations.schemas import OrganizationOut
from src.branches.schemas import BranchMinimal
from typing import Optional, Self



class BranchAccessMixin(BaseModel):
    allowed_branch_ids: list[int] = Field(..., example=[1, 2, 3], description="Branches the user or role is allowed to access")

    @field_validator("allowed_branch_ids")
    @classmethod
    def validate_branches(cls, v: list[int]):
        if len(v) == 0:
            raise ValueError("At least one branch must be allowed.")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate branch IDs are not allowed.")
        return v

class PermissionMixin(BaseModel):
    permissions: list[str] = Field(..., example=["invoices:read", "invoices:create"])
    
    @model_validator(mode="after")
    def validate_permissions(self) -> Self:
        if len(self.permissions) == 0:
            raise ValueError("The permissions list cannot be empty.")
        for perm in self.permissions:
            try:
                resource, action = perm.split(":")
                if resource.strip() == "" or action.strip() == "":
                    raise ValueError("Invalid permission format: {perm}. Expected format 'resource:action'. Resource and action cannot be empty.")
            except ValueError:
                raise ValueError(f"Invalid permission format: {perm}. Expected format 'resource:action'.")
        return self
    
class UserPermissionCreate(PermissionMixin, BranchAccessMixin):
    pass

class UserPermissionUpdate(PermissionMixin, BranchAccessMixin):
    pass

class UserPermissionOut(PermissionMixin):
    allowed_branches: list[BranchMinimal]


class PermissionInDB(BaseModel):
    id: int
    resource: str
    action: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UserPermissionCreateInternal(BaseModel):
    user_id: int
    organization_id: int
    permission_id: int
    is_allowed: bool




class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)

class RoleCreate(RoleBase, PermissionMixin):
    pass


class RoleUpdate(RoleBase, PermissionMixin):
    pass
    
class RoleInDB(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RoleWithPermissionsOut(RoleBase, PermissionMixin):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RolePermissionCreateInternal(BaseModel):
    role_id: int
    organization_id: int
    permission_id: int
    is_allowed: bool
