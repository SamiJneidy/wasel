from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from decimal import Decimal
from src.core.schemas import AuditTimeMixin, ObjectListResponse, SingleObjectResponse
from src.core.enums import TaxScheme, UnitCodes
from typing import Optional


class BranchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=300, example="Wasel LLC")
    phone: str = Field(..., min_length=10, max_length=15, example="+966121234567")
    street: Optional[str] = Field(..., min_length=1, max_length=300, example="Tahlia Stree", description="This field is free text")
    building_number: Optional[str] = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$", example="1234")
    division: Optional[str] = Field(..., min_length=1, max_length=200, example="Albawadi")
    city: Optional[str] = Field(..., min_length=1, max_length=50, example="Jeddah")
    postal_code: Optional[str] = Field(..., min_length=5, max_length=5, pattern=r"^\d{5}$")
    address: Optional[str] = Field(..., example="City - District - Street Name", description="This field is free text, the pattern in the example is not mandatory. You don't have to be restricted with a specific pattern.")
    
class BranchCreate(BranchBase):
    pass

class BranchUpdate(BranchBase):
    pass

class BranchOut(BranchBase):
    id: int
    model_config = ConfigDict(from_attributes=True)