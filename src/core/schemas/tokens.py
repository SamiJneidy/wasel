from pydantic import BaseModel
from datetime import datetime
from ..enums import TokenScope
from typing import Optional

class TokenPayloadBase(BaseModel):
    sub: str
    scope: TokenScope
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None


class AccessTokenPayload(TokenPayloadBase):
    scope: TokenScope = TokenScope.ACCESS


class RefreshTokenPayload(TokenPayloadBase):
    scope: TokenScope = TokenScope.REFRESH


class UserInviteTokenPayload(TokenPayloadBase):
    invited_by: int
    organization_id: int
    scope: TokenScope = TokenScope.INVITE


class ResetPasswordTokenPayload(TokenPayloadBase):
    scope: TokenScope = TokenScope.RESET_PASSWORD
