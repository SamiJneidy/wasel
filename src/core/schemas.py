from datetime import datetime
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, Field

T = TypeVar("T")

class SingleObjectResponse(BaseModel, Generic[T]):
    """Used when returning a single object"""
    data: T = Field(..., description="This may be any schema value")
    
class PagintationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: Optional[int] = Field(None, ge=1, le=100)

    @property
    def skip(self):
        if self.page is not None and self.limit is not None:
            return (self.page-1) * self.limit
        return None

class PaginatedResponse(BaseModel, Generic[T]):
    """Used when returning paginated data"""
    data: list[T]
    total_rows: int | None = None
    total_pages: int | None = None
    page: int | None = None
    limit: int | None = None

class ObjectListResponse(BaseModel, Generic[T]):
    """Used when returning an array of objects"""
    data: list[T] = Field(..., description="This may be any schema value")

class SuccessfulResponse(BaseModel):
    detail: str

class ErrorResponse(BaseModel):
    detail: str

class AuditByMixin:
    """Adds created_by and updated_by columns to a schema."""
    created_by: int | None
    updated_by: int | None

class AuditTimeMixin:
    """Adds created_at and updated_at columns to a schema."""
    created_at: datetime
    updated_at: datetime | None

class AuditMixin(AuditByMixin, AuditTimeMixin):
    """Adds created_at, created_by, updated_at and updated_by to a schema."""
    pass

class BaseSchema(AuditMixin):
    """This is the main schema. It adds id, created_at, created_by, updated_at and updated_by to a schema."""
    id: int