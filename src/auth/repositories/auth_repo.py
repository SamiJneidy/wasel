from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, select, insert, update, delete
from ..models import User

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_user(self, email: str) -> None:
        """Deletes a user from the database. Note that this is NOT a soft delete, this will delete the user permanently from the database."""
        stmt = delete(User).where(User.email==email)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
