from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import datetime
from src.zatca.schemas import ZatcaCSIDResponse
from src.core.schemas import AuditTimeMixin
from src.users.schemas import UserOut
from src.core.enums import CSIDType
from typing import Optional


class CSIDCreate(ZatcaCSIDResponse):
    user_id: int
    type: CSIDType
    private_key: str
    csr_base64: str
    certificate: str
    authorization: str


class ComplianceCSIDRequest(BaseModel):
    code: str

    @field_validator('otp', mode='after')
    def is_numeric(cls, value):
        if not value.isnumeric():
            raise ValueError("OTP value must be numeric")
        return value


class ComplianceCSIDResponse(BaseModel):
    email: EmailStr