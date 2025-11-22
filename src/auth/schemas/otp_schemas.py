from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from src.core.enums import OTPStatus, OTPUsage

class OTPBase(BaseModel):
    email: EmailStr 
    usage: OTPUsage 
    expires_at: datetime


class OTPCreate(OTPBase):
    pass


class OTPOut(OTPBase):
    code: str
    status: OTPStatus
    model_config = ConfigDict(from_attributes=True)
