from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from src.core.enums import ProjectStatus
from src.customers.schemas import CustomerOut

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=300, example="Website Development")
    description: Optional[str] = Field(None, min_length=1, max_length=1000, example="Project for building company website")
    status: ProjectStatus = Field(..., example="active")
    start_date: Optional[date] = Field(None, example="2026-01-01")
    end_date: Optional[date] = Field(None, example="2026-06-30")
    budget_amount: Optional[float] = Field(None, example=50000.00)


class ProjectCreate(ProjectBase):
    customer_id: Optional[int] = Field(None, example=1)


class ProjectUpdate(ProjectCreate):
    pass


class ProjectOut(ProjectBase):
    id: int
    customer: Optional[CustomerOut] = None
    model_config = ConfigDict(from_attributes=True)


class ProjectFilters(BaseModel):
    name: Optional[str] = Field(None, example="Website")
    status: Optional[ProjectStatus] = Field(None)
    customer_id: Optional[int] = Field(None, example=1)
