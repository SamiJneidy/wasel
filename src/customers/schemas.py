from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin, ObjectListResponse, SingleObjectResponse
from src.users.schemas import UserOut
from src.core.enums import PartyIdentificationScheme
from typing import Optional


class CustomerBase(BaseModel):
    registration_name: str = Field(..., min_length=1, max_length=250, example="Wasel LLC")
    vat_number: str = Field(..., min_length=15, max_length=15, pattern=r"^3\d{13}3$")
    street: str = Field(..., min_length=1, max_length=300, example="Tahlia Street", description="This field is free text")
    building_number: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$", example="1234")
    division: str = Field(..., min_length=1, max_length=200, example="Albawadi")
    city: str = Field(..., min_length=1, max_length=50, example="Jeddah")
    postal_code: str = Field(..., min_length=5, max_length=5, pattern=r"^\d{5}$")
    party_identification_scheme: PartyIdentificationScheme
    party_identification_value: str = Field(..., min_length=1, max_length=25, example="5243526715")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)