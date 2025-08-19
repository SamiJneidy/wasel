from typing import Self
from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, Field, model_validator
from datetime import datetime
from src.core.schemas import BaseSchema, SingleObjectResponse, SuccessfulResponse, ErrorResponse
from src.users.schemas import UserOut, UserUpdate
from src.core.enums import OTPStatus, OTPUsage, UserRole, UserStatus

# Authentication

class TokenPayload(BaseModel):
    sub: str
    iat: datetime | None = None
    exp: datetime | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str


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


class SignUpCompleteRequest(UserUpdate):
    pass


class SignUpCompleteResponse(UserOut):
    pass


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123")


class LoginResponse(BaseModel):
    user: UserOut
    access_token: str


class RequestEmailVerificationOTPRequest(BaseModel):
    email: EmailStr


class RequestEmailVerificationOTPResponse(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    code: str = Field(..., example="123456")


class VerifyEmailResponse(BaseModel):
    email: EmailStr


class RequestPasswordResetOTPRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    

class RequestPasswordResetOTPResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


class VerifyPasswordResetOTPRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    code: str = Field(..., example="123456")
    

class VerifyPasswordResetOTPResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    confirm_password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class ResetPasswordResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


# OTP
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

