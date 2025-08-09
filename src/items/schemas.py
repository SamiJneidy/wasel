from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from decimal import Decimal
from src.core.schemas import AuditTimeMixin, ObjectListResponse, SingleObjectResponse
from src.users.schemas import UserOut
from src.core.enums import UnitCodes
from typing import Optional


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=250, example="Cola")
    price: Decimal = Field(..., decimal_places=2, example="10.15")
    unit_code: UnitCodes = Field(..., min_length=1, max_length=15, example="PCE")

    @field_validator("price", mode="after")
    def is_positive(cls, value):
        if value <= 0:
            raise ValueError("The price should be positive and greater than zero")
        return value

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemOut(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)