from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin, ObjectListResponse, SingleObjectResponse
from src.users.schemas import UserOut
from src.core.enums import PartyIdentificationScheme
from typing import Optional


class SupplierBase(BaseModel):
    registration_name: str = Field(..., min_length=1, max_length=250, example="Wasel LLC")
    vat_number: Optional[str] = Field(None, min_length=15, max_length=15, pattern=r"^3\d{13}3$")
    street: Optional[str] = Field(None, min_length=1, max_length=300, example="Tahlia Street", description="This field is free text")
    building_number: Optional[str] = Field(None, min_length=4, max_length=4, pattern=r"^\d{4}$", example="1234")
    division: Optional[str] = Field(None, min_length=1, max_length=200, example="Albawadi")
    city: Optional[str] = Field(None, min_length=1, max_length=50, example="Jeddah")
    postal_code: Optional[str] = Field(None, min_length=5, max_length=5, pattern=r"^\d{5}$")
    party_identification_scheme: Optional[PartyIdentificationScheme] = None
    party_identification_value: Optional[str] = Field(None, min_length=1, max_length=25, example="5243526715")
    phone: Optional[str] = Field(None, example="+963900000000")
    website: Optional[str] = Field(None, min_length=1, max_length=100, example="www.wasel.com")
    bank_account: Optional[str] = Field(None, min_length=1, max_length=100, example="11111111111111")
    notes: Optional[str] = Field(None, min_length=1, max_length=1000, example="Extra information")



class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierOut(SupplierBase):
    id: int
    model_config = ConfigDict(from_attributes=True)