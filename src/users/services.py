from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from src.organizations.exceptions import OrganizationNotFoundException
from .repositories import UserRepository
from .schemas import (
    UserOut,
    UserUpdate,
    UserInDB,
    UserInvite,
    UserInviteTokenPayload,
    UserCreate,
)
from .exceptions import (
    InvitationNotAllowedException,
    UserNotFoundException,
    UserNotActiveException,
    UserAlreadyExistsException,
)
from src.organizations.services import OrganizationService
from src.auth.services.token_service import TokenService
from src.core.services import EmailService
from src.core.config import settings
from src.core.enums import UserStatus, UserType


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        email_service: EmailService,
        token_service: TokenService,
        organization_service: OrganizationService,
    ):
        self.user_repo = user_repo
        self.email_service = email_service
        self.token_service = token_service
        self.organization_service = organization_service

    async def _get_or_raise_by_email(self, email: str) -> UserInDB:
        db_user = await self.user_repo.get_by_email(email)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)

    async def _get_or_raise_by_id(self, id: int) -> UserInDB:
        db_user = await self.user_repo.get(id)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)

    async def get(self, id: int) -> UserInDB:
        return await self._get_or_raise_by_id(id)

    async def get_user_out(self, email: str) -> UserOut:
        user = await self._get_or_raise_by_email(email)
        user_out = UserOut.model_validate(user)
        try:
            user_org = await self.organization_service.get_organization(user.organization_id)
        except OrganizationNotFoundException:
            user_org = None
        user_out.organization = user_org
        return user_out

    async def get_by_email(self, email: str) -> UserInDB:
        return await self._get_or_raise_by_email(email)

    async def get_users_by_org_id(self, org_id: int) -> UserInDB:
        return await self.user_repo.get_users_by_org(org_id)
    
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

    async def invite_user(self, current_user: UserInDB, host_url: str, invite: UserInvite) -> UserInDB:
        if await self.user_repo.get_by_email(invite.email):
            raise UserAlreadyExistsException()
        create_payload = {
            **invite.model_dump(exclude_none=True),
            "organization_id": current_user.organization_id,
            "type": UserType.CLIENT,
            "status": UserStatus.PENDING,
            "is_completed": False,
        }
        user = await self.user_repo.create(create_payload)
        await self.send_invitation(current_user, invite.email, host_url)
        return UserInDB.model_validate(user)

    async def send_invitation(self, inviter: UserInDB, email: str, host_url: str) -> None:
        user = await self.get_by_email(email)
        if user.is_completed or user.status != UserStatus.PENDING:
            raise InvitationNotAllowedException()
        now = datetime.now(tz=timezone.utc)
        payload = UserInviteTokenPayload(
            sub=email,
            iat=now,
            exp=now + timedelta(minutes=settings.USER_INVITATION_TOKEN_EXPIRATION_MINUTES),
            invited_by=inviter.id,
            organization_id=inviter.organization_id,
            scope="invitation",
        )
        token = self.token_service.create_token(payload.model_dump())
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
