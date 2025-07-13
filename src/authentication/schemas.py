from typing import Self
from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, Field, model_validator
from datetime import datetime
from src.core.schemas import BaseSchema
from src.core.enums import OTPStatus, OTPUsage, UserRole, UserStatus
from src.users.schemas import UserOut

# Authentication Schemas
class SignUp(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    confirm_password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
    
class SignUpResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    model_config = ConfigDict(from_attributes=True)

class Login(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="acc", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class LoginResponse(TokenResponse):
    pass

class LogoutResponse(BaseModel):
    detail: str = Field(..., example="Logged out successfully")

class TokenPayload(BaseModel):
    sub: str
    iat: datetime | None = None
    exp: datetime | None = None

class Login(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123")

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    confirm_password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")

class PasswordResetResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class EmailVerificationOTPRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    
class EmailVerificationOTPResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class PasswordResetOTPRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    
class PasswordResetOTPResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

# OTP Schemas
class OTPBase(BaseModel):
    email: EmailStr 
    code: str
    usage: OTPUsage 
    status: OTPStatus
    expires_at: datetime

class OTPCreate(OTPBase):
    pass

class OTPOut(OTPBase):
    model_config = ConfigDict(from_attributes=True)

class OTPVerificationRequest(BaseModel):
    code: str = Field(..., example="1234656")

class OTPVerificationResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
