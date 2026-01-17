from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin
from src.organizations.schemas import OrganizationOut
from src.branches.schemas import BranchOut
from src.core.enums import UserRole, UserStatus, UserType
from typing import Optional, Self

class PermissionOut(BaseModel):
    id: int
    resource: str
    action: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserPermissionBase(BaseModel):
    permissions: list[str] = Field(..., example=["invoices:read", "invoices:create"])
    
    @model_validator(mode="after")
    def validate_permissions(self) -> Self:
        for perm in self.permissions:
            try:
                resource, action = perm.split(":")
                if resource.strip() == "" or action.strip() == "":
                    raise ValueError("Invalid permission format: {perm}. Expected format 'resource:action'. Resource and action cannot be empty.")
            except ValueError:
                raise ValueError(f"Invalid permission format: {perm}. Expected format 'resource:action'.")
        return self
    
    model_config = ConfigDict(from_attributes=True)
    
class UserPermissionCreateInternal(BaseModel):
    user_id: int
    organization_id: int
    permission_id: int
    is_allowed: bool

class UserPermissionCreate(UserPermissionBase):
    pass

class UserPermissionUpdate(UserPermissionCreate):
    pass

class UserPermissionOut(UserPermissionBase):
    pass