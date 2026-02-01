from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from src.organizations.exceptions import OrganizationNotFoundException
from .repositories import UserRepository
from .schemas import (
    UserOut,
    UserUpdate,
    UserInDB,
    UserInvite,
    UserCreate,
    UserFilters
)
from src.auth.schemas.token_schemas import UserInviteToken
from .exceptions import (
    InvitationNotAllowedException,
    UserNotFoundException,
    UserNotActiveException,
    UserAlreadyExistsException,
)
from src.core.schemas import PagintationParams
from src.organizations.services import OrganizationService
from src.auth.services.token_service import TokenService
from src.core.services import EmailService
from src.core.config import settings
from src.core.enums import UserStatus, UserType
from src.authorization.services.authorization_service import AuthorizationService
from src.authorization.schemas import UserPermissionCreate
from src.core.schemas.context import RequestContext
from src.branches.schemas import BranchMinimal
from src.branches.repositories import BranchRepository

class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        email_service: EmailService,
        token_service: TokenService,
        organization_service: OrganizationService,
        authorization_service: AuthorizationService,
    ):
        self.user_repo = user_repo
        self.email_service = email_service
        self.token_service = token_service
        self.organization_service = organization_service
        self.authorization_service = authorization_service

    async def _get_or_raise_by_email(self, email: str) -> UserInDB:
        db_user = await self.user_repo.get_by_email(email)
        if not db_user:
            raise UserNotFoundException()
        user_in_db = UserInDB.model_validate(db_user)
        return UserInDB.model_validate(user_in_db)

    async def _get_or_raise_by_id(self, id: int) -> UserInDB:
        db_user = await self.user_repo.get(id)
        if not db_user:
            raise UserNotFoundException()
        user_in_db = UserInDB.model_validate(db_user)
        return UserInDB.model_validate(user_in_db)

    async def get_user_in_db(self, email: str) -> UserInDB:
        user = await self._get_or_raise_by_email(email)
        return UserInDB.model_validate(user)

    async def get_user(self, id: int) -> UserOut:
        user = await self._get_or_raise_by_id(id)
        return UserOut.model_validate(user)
    
    async def get_user_by_email(self, email: str) -> UserOut:
        user = await self._get_or_raise_by_email(email)
        return UserOut.model_validate(user)

    async def get_users(self, ctx: RequestContext, pagination_params: PagintationParams, filters: UserFilters) -> tuple[int, list[UserOut]]:
        total, query_set = await self.user_repo.get_users_by_org(
            ctx.organization.id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [UserOut.model_validate(user) for user in query_set]
    
    async def create_user(self, payload: UserCreate) -> UserInDB:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise UserAlreadyExistsException()
        data = payload.model_dump()
        user = await self.user_repo.create(data)
        return UserInDB.model_validate(user)

    async def update_by_email(self, email: str, update_data: Dict[str, Any]) -> UserInDB:
        db_user = await self.user_repo.update_by_email(email, update_data)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)

    async def invite_user(self, ctx: RequestContext, host_url: str, invite: UserInvite) -> UserInDB:
        if await self.user_repo.get_by_email(invite.email):
            raise UserAlreadyExistsException()
        # Validate role
        role = await self.authorization_service.get_role(ctx, invite.role_id)
        if role.name == "SUPER_ADMIN":
            raise InvitationNotAllowedException(detail="Cannot invite user with SUPER_ADMIN role.")
        create_payload = {
            **invite.model_dump(exclude={"permissions"}, exclude_none=True),
            "organization_id": ctx.organization.id,
            "type": UserType.CLIENT,
            "status": UserStatus.PENDING,
            "is_completed": False,
        }
        created_user = await self.user_repo.create(create_payload)
        await self.authorization_service.create_user_permissions(ctx, created_user.id, invite.access)
        await self.send_invitation(ctx.user, invite.email, host_url)
        return await self.get_user_by_email(created_user.email)

    async def send_invitation(self, inviter: UserOut, email: str, host_url: str) -> None:
        user = await self.get_user_by_email(email)
        if user.is_completed or user.status != UserStatus.PENDING:
            raise InvitationNotAllowedException()
        payload = UserInviteToken(
            sub=email,
            invited_by=inviter.id,
            organization_id=inviter.organization_id,
        )
        token = self.token_service.create_user_invitation_token(payload)
        if not host_url.endswith("/"):
            host_url = host_url + "/"
        url = f"{host_url}user-onboarding?token={token}"
        await self.email_service.send_user_invitation(email, url)
        return None

    async def increment_invalid_login_attempts(self, email: str) -> UserInDB:
        db_user = await self.user_repo.increment_invalid_login_attempts(email)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)

    async def reset_invalid_login_attempts(self, email: str) -> UserInDB:
        db_user = await self.user_repo.reset_invalid_login_attempts(email)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)

    async def update_user_status(self, email: str, status: UserStatus) -> UserInDB:
        db_user = await self.user_repo.update_user_status(email, status)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)

    async def update_last_login(self, email: str, last_login: datetime) -> UserInDB:
        db_user = await self.user_repo.update_last_login(email, last_login)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)

    async def delete_user(self, email: str) -> None:
        await self._get_or_raise_by_email(email)
        await self.user_repo.delete_by_email(email)
        return None
