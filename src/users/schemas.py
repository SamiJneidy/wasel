from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin
from src.organizations.schemas import OrganizationOut
from src.core.enums import UserRole, UserStatus, UserType
from typing import Optional

class UserBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=100, example="user@example.com")

class UserUpdate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    organization: Optional[OrganizationOut] = None
    is_completed: bool
    status: UserStatus
    role: UserRole
    type: UserType
    last_login: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserOut):
    password: str
    last_login: Optional[datetime]
    invalid_login_attempts: int
    role: UserRole
    model_config = ConfigDict(from_attributes=True)
