from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.core.schemas import AuditTimeMixin
from src.users.schemas import UserOut
from src.core.enums import CSIDType
from typing import Optional


class CSIDBase(BaseModel):
    user_id: int
    type: CSIDType
    request_id: str
    disposition_message: str
    binary_security_token: str
    secret: str
    private_key: str
    csr_base64: str
    certificate: str
    authorization: str


class CSIDCreate(CSIDBase):
    pass


class CSIDInDB(CSIDBase):
    model_config = ConfigDict(from_attributes=True)


class ComplianceCSIDRequest(BaseModel):
    code: str = Field(..., pattern=r'^\d{6}$', description="The OTP code from Zatca portal")


class CSIDOut(BaseModel):
    email: EmailStr