from datetime import datetime, timedelta, timezone
from src.core.enums import UserStatus, UserType
from src.core.services import EmailService, TokenService
from src.core.config import settings
from .repositories import UserRepository
from .schemas import UserOut, UserUpdate, UserInDB, UserInviteRequest, UserInviteTokenPayload
from .exceptions import InvitationNotAllowedException, UserNotFoundException, UserNotActiveException, UserAlreadyExistsException

class UserService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service

    
    async def get(self, id: int) -> UserOut:
        """Returns user by id."""
        db_user = await self.user_repo.get(id)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)
    

    async def get_by_email(self, email: str) -> UserOut:
        """Returns user by email."""
        db_user = await self.user_repo.get_by_email(email)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)

    
    async def get_user_in_db(self, email: str) -> UserInDB:
        """Returns full user object. This may leak sensitive information."""
        db_user = await self.user_repo.get_by_email(email)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)


    async def create_user(self, data: dict) -> UserOut:
        db_user = await self.user_repo.create(data)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)


    async def update_by_email(self, email: str, data: dict) -> UserOut:
        """Updates a user. This methods accepts the data as 'dict'."""
        db_user = await self.user_repo.update_by_email(email, data)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)
    

    async def invite_user(self, current_user_email: str, host_url: str, data: UserInviteRequest) -> UserOut:
        try:
            user = await self.get_by_email(data.email)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass
        current_user = await self.get_by_email(current_user_email)
        user_dict = data.model_dump()
        user_dict.update({
            "organization_id": current_user.organization.id,
            "type": UserType.CLIENT, 
            "status": UserStatus.PENDING, 
            "is_completed": False
        })
        await self.create_user(user_dict)
        await self.send_invitation(data.email, host_url)
        return await self.get_by_email(data.email)


    async def send_invitation(self, email: str, host_url: str) -> UserOut:
        user = await self.get_by_email(email)
        if user.is_completed == True or user.status != UserStatus.PENDING:
            raise InvitationNotAllowedException()
        payload = UserInviteTokenPayload(
            sub=email, 
            iat = datetime.now(tz=timezone.utc),
            exp=datetime.now(tz=timezone.utc) + timedelta(minutes=settings.USER_INVITATION_TOKEN_EXPIRATION_MINUTES)
        )
        token = TokenService.create_token(payload.model_dump())
        url = f"{host_url}user-onboarding?token={token}"
        await self.email_service.send_user_invitation(email, url)
        return user

    
    async def increment_invlaid_login_attempts(self, email: str) -> UserInDB:
        """Increments the number of invalid login attempts for a user by 1."""
        db_user = await self.user_repo.increment_invalid_login_attempts(email)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.model_validate(db_user)
    
    
    async def reset_invalid_login_attempts(self, email: str) -> UserOut:
        """Resets the number of invalid login attempts for a user to zero."""
        db_user = await self.user_repo.reset_invalid_login_attempts(email)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)
    
    
    async def update_user_status(self, email: str, status: UserStatus) -> UserOut:
        """Updates user status."""
        db_user = await self.user_repo.update_user_status(email, status)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)
    
    
    async def update_last_login(self, email: str, last_login: datetime) -> UserOut:
        """Updates user status."""
        db_user = await self.user_repo.update_last_login(email, last_login)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)
    

    async def delete_user(self, email: str) -> None:
        """Deletes a user (NOT A SOFT DELETE)."""
        db_user = await self.get_by_email(email)
        if not db_user:
            raise UserNotFoundException()
        await self.user_repo.delete(email)
        return None
    