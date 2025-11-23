from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from decimal import Decimal
from src.core.enums import UnitCodes
from typing import Optional


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=250, example="Cola")
    default_sale_price: Decimal = Field(..., decimal_places=2, example="10.15")
    default_buy_price: Decimal = Field(..., decimal_places=2, example="10.15")
    unit_code: UnitCodes = Field(..., min_length=1, max_length=15, example="PCE")
    description: Optional[str] = Field(..., min_length=1, max_length=200)

    @field_validator("default_sale_price", "default_buy_price", mode="after")
    def is_positive(cls, value):
        if value < 0:
            raise ValueError("The price should be positive")
        return value

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemOut(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ItemFilters(BaseModel):
    name: Optional[str] = None
