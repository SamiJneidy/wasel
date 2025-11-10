from datetime import datetime
from src.core.enums import UserStatus
from .repositories import UserRepository
from .schemas import UserOut, UserUpdate, UserInDB
from .exceptions import UserNotFoundException, UserNotActiveException

class UserService:
    def __init__(self, 
        user_repo: UserRepository,
    ):
        self.user_repo = user_repo

    
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


    async def create_user_after_signup(self, data: dict) -> UserOut:
        """Creates an initial user after signup. The user will need verification to continue the sigup process. This methos accepts the data as 'dict'."""
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
    