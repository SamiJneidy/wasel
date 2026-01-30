from pydantic import BaseModel, model_validator
from datetime import datetime
from src.core.enums import TokenScope
from typing import Optional, Self
from src.authorization.schemas import UserPermissionOut
from src.branches.schemas import BranchOut

class TokenPayloadBase(BaseModel):
    scope: TokenScope
    sub: int
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None

class AccessToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.ACCESS
    branch_id: int
    organization_id: int
    permissions: Optional[list[str]] = None

    @model_validator(mode="after")
    def parse_str(self) -> Self:
        self.sub = str(self.sub)
        self.branch_id = str(self.branch_id)
        self.organization_id = str(self.organization_id)
        return self

class RefreshToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.REFRESH
    branch_id: int
    organization_id: int
    
    @model_validator(mode="after")
    def parse_str(self) -> Self:
        self.sub = str(self.sub)
        self.branch_id = str(self.branch_id)
        self.organization_id = str(self.organization_id)
        return self


class SignUpCompleteToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.SIGN_UP_COMPLETE


class UserInviteToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.INVITE
    invited_by: int
    organization_id: int


class PasswordResetToken(TokenPayloadBase):
    scope: TokenScope = TokenScope.RESET_PASSWORD
