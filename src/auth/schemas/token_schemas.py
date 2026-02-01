from pydantic import BaseModel, field_validator
from datetime import datetime
from src.core.enums import TokenScope
from typing import Optional, Self

class TokenPayloadBase(BaseModel):
    scope: TokenScope
    sub: int
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None
    
    @field_validator("sub", mode="after")
    def sub_to_str(cls, value) -> Self:
        return str(value)


class AccessToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.ACCESS
    branch_id: int
    organization_id: int


class RefreshToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.REFRESH
    branch_id: int
    organization_id: int

class SignUpCompleteToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.SIGN_UP_COMPLETE


class UserInviteToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.INVITE
    invited_by: int
    organization_id: int


class PasswordResetToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.RESET_PASSWORD
