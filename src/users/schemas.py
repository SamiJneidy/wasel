from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin
from src.core.enums import PartyIdentificationScheme, UserRole, UserStatus, Stage, InvoicingType
from typing import Optional

class UserBase(BaseModel):
    email: str = Field(..., min_length=5, max_length=100, example="user@example.com")

class UserUpdate(UserBase):
    pass

class UserOut(UserBase, AuditTimeMixin):
    id: int
    organization_id: Optional[int] = None
    is_completed: bool = Field(..., description="A boolean to identify if the user has finished the signup process or not. The signup process ends when the user successfully enters his company info.")
    status: UserStatus
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserOut):
    password: str
    last_login: Optional[datetime]
    invalid_login_attempts: int
    role: UserRole
    model_config = ConfigDict(from_attributes=True)
