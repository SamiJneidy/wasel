from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from decimal import Decimal
from src.core.enums import UnitCodes
from typing import Optional


class PointOfSaleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=250, example="Point of sale 1")

class PointOfSaleCreate(PointOfSaleBase):
    pass

class PointOfSaleUpdate(PointOfSaleBase):
    pass

class PointOfSaleOut(PointOfSaleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PointOfSaleFilters(BaseModel):
    name: Optional[str] = None
