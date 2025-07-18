from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin
from src.core.enums import PartyIdentificationScheme, UserRole, UserStatus
from typing import Optional

class UserBase(BaseModel):
    phone: Optional[str] = Field(..., min_length=10, max_length=15, example="+966121234567")
    registraion_name: Optional[str] = Field(..., min_length=1, max_length=250, example="Wasel LLC")
    vat_number: Optional[str] = Field(..., min_length=15, max_length=15, pattern=r"^3\d{13}3$")
    invoicing_type: Optional[str] = Field(..., min_length=4, max_length=4, pattern=r"^[0-1]{2}00$")
    address: Optional[str] = Field(..., example="City - District - Street Name", description="This field is free text, the pattern in the example is not mandatory. You don't have to be restricted with a specific pattern.")
    business_category: Optional[str] = Field(..., min_length=1, max_length=100, example="Education", description="This field is free text")
    street: Optional[str] = Field(..., min_length=1, max_length=300, example="Tahlia Stree", description="This field is free text")
    building_number: Optional[str] = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$", example="1234")
    division: Optional[str] = Field(..., min_length=1, max_length=200, example="Albawadi")
    city: Optional[str] = Field(..., min_length=1, max_length=50, example="Jeddah")
    postal_code: Optional[str] = Field(..., min_length=5, max_length=5, pattern=r"^\d{5}$")
    party_identification_scheme: Optional[PartyIdentificationScheme]
    party_identification_value: Optional[str] = Field(..., min_length=1, max_length=25, example="5243526715")

class UserUpdate(UserBase):
    pass

class UserOut(UserBase, AuditTimeMixin):
    email: str = Field(..., min_length=5, max_length=100, example="user@example.com")
    status: UserStatus
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    email: str
    password: str
    country_code: Optional[str]
    common_name: Optional[str]
    organization_unit_name: Optional[str]
    organization_name: Optional[str]
    last_login: Optional[datetime]
    invalid_login_attempts: int
    status: UserStatus
    role: UserRole
    model_config = ConfigDict(from_attributes=True)
    