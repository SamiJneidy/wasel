from src.core.enums import UserStatus
from .repositories import UserRepository
from .schemas import (
    UserOut,
    UserUpdate,
)
from .exceptions import (
    UserNotFoundException,
    UserNotActiveException,
)

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

    async def update(self, id: int, data: UserUpdate) -> UserOut:
        """Updates user by id."""
        data_dict = data.model_dump()
        data_dict.update({"common_name": data.registraion_name, "organization_name": data.registraion_name, "country_code": "SA"})
        
        if data.vat_number[10] == "1":
            tin_number = data.vat_number[:10]
            data_dict.update({"organization_unit_name": tin_number})    
        else:
            data_dict.update({"organization_unit_name": data.registraion_name})

        db_user = await self.user_repo.update(id, data_dict)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)

    async def update_by_email(self, email: str, data: UserUpdate) -> UserOut:
        """Updates user by email."""
        data_dict = data.model_dump()
        data_dict.update({"common_name": data.registraion_name, "organization_name": data.registraion_name, "country_code": "SA"})
        
        if data.vat_number[10] == "1":
            tin_number = data.vat_number[:10]
            data_dict.update({"organization_unit_name": tin_number})    
        else:
            data_dict.update({"organization_unit_name": data.registraion_name})

        db_user = await self.user_repo.update_by_email(email, data_dict)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)
    
    async def increment_invlaid_login_attempts(self, email: str) -> UserOut:
        """Increments the number of invalid login attempts for a user by 1."""
        db_user = await self.user_repo.increment_invalid_login_attempts(email)
        if not db_user:
            raise UserNotFoundException()
        return UserOut.model_validate(db_user)
    
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
    
    async def delete_user(self, email: str) -> None:
        """Deletes a user (NOT A SOFT DELETE)."""
        db_user = await self.get_by_email(email)
        if not db_user:
            raise UserNotFoundException()
        await self.user_repo.delete(email)
        return None