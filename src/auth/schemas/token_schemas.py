from pydantic import BaseModel
from datetime import datetime
from src.core.enums import TokenScope
from typing import Optional

class TokenPayloadBase(BaseModel):
    sub: str
    scope: TokenScope
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None


class AccessToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.ACCESS


class RefreshToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.REFRESH


class SignUpCompleteToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.SIGN_UP_COMPLETE


class UserInviteToken(TokenPayloadBase):
    invited_by: int
    organization_id: int
    scope: TokenScope = TokenScope.INVITE


class PasswordResetToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.RESET_PASSWORD
