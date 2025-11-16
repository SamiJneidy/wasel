from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, update, delete, insert, func
from src.core.database import AsyncSession

from .models import User
from src.core.enums import UserStatus


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[User]:
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.email) == email.lower())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create(self, data: dict) -> User:
        user = User(**data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_by_id(self, id: int, data: dict) -> Optional[User]:
        stmt = (
            update(User)
            .where(User.id == id)
            .values(**data)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def update_by_email(self, email: str, data: Dict[str, Any]) -> Optional[User]:
        stmt = (
            update(User)
            .where(func.lower(User.email) == email.lower())
            .values(**data)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def increment_invalid_login_attempts(self, email: str) -> Optional[User]:
        stmt = (
            update(User)
            .where(func.lower(User.email) == email.lower())
            .values(invalid_login_attempts=User.invalid_login_attempts + 1)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def reset_invalid_login_attempts(self, email: str) -> Optional[User]:
        stmt = (
            update(User)
            .where(func.lower(User.email) == email.lower())
            .values(invalid_login_attempts=0)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def update_user_status(self, email: str, status: UserStatus) -> Optional[User]:
        stmt = (
            update(User)
            .where(func.lower(User.email) == email.lower())
            .values(status=status)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def verify_user(self, email: str) -> Optional[User]:
        return await self.update_user_status(email, UserStatus.ACTIVE)

    async def update_last_login(self, email: str, last_login: datetime) -> Optional[User]:
        stmt = (
            update(User)
            .where(func.lower(User.email) == email.lower())
            .values(last_login=last_login)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def delete_by_email(self, email: str) -> None:
        stmt = delete(User).where(func.lower(User.email) == email.lower())
        await self.db.execute(stmt)
        return None
