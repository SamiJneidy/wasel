from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin
from src.organizations.schemas import OrganizationOut
from src.branches.schemas import BranchOut
from src.core.enums import UserRole, UserStatus, UserType
from src.authorization.schemas import UserPermissionCreate
from typing import Optional, Self

class UserInDB(BaseModel, AuditTimeMixin):
    id: int
    organization_id: Optional[int] = None
    branch_id: Optional[int] = None
    name: str
    phone: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None
    role: UserRole
    is_completed: bool
    status: UserStatus
    type: UserType
    last_login: Optional[datetime] = None
    invalid_login_attempts: int = 0
    organization: Optional[OrganizationOut] = None
    branch: Optional[BranchOut] = None
    permissions: Optional[list[str]] = None
    model_config = ConfigDict(from_attributes=True)

    
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=100, example="user@example.com")
    role: UserRole = Field(..., example=UserRole.SALESMAN) 


class UserCreate(UserBase):
    organization_id: Optional[int] = None
    password: str = Field(..., min_length=8, max_length=128)
    status: UserStatus = UserStatus.PENDING
    type: UserType = UserType.CLIENT
    is_completed: bool = False

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class UserOut(UserBase):
    id: int
    organization: Optional[OrganizationOut] = None
    branch: Optional[BranchOut] = None
    permissions: Optional[list[str]] = None
    is_completed: bool
    status: UserStatus
    type: UserType
    last_login: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class UserInvite(UserPermissionCreate):
    branch_id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    
    @field_validator("role", mode="after")
    def check_role(cls, value):
        if value == UserRole.SUPER_ADMIN:
            raise ValueError("Role cannot be SUPER_ADMIN")
        return value   

    @field_validator("email", mode="after")
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower() 


class UserFilters(BaseModel):
    name: Optional[str] = Field(None, example="User Name")
    email: Optional[str] = Field(None)
    phone: Optional[str] = Field(None, example="+963900000000")
    role: Optional[UserRole] = None
