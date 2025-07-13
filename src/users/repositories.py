from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from datetime import datetime
from .models import User
from src.core.enums import UserRole, UserStatus, OTPUsage, OTPStatus

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get(self, id: int) -> User | None:
        """Get user by id."""
        return self.db.query(User).filter(User.id==id).first()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.db.query(User).filter(User.email==email).first()

    async def create(self, data: dict) -> User | None:
        """Create a new user."""
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def update(self, id: int, data: dict) -> User | None:
        """Update user by id."""
        stmt = update(User).where(User.id==id).values(**data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get(id)
    
    async def update_by_email(self, email: str, data: dict) -> User | None:
        """Update user by email."""
        stmt = update(User).where(User.email==email).values(**data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get_by_email(email)
    
    async def increment_invalid_login_attempts(self, email: str) -> User | None:
        """Increments the number of invalid login attempts for a user by 1."""
        db_user: User = self.db.query(User).filter(User.email==email).first()
        if not db_user:
            return None
        db_user.invalid_login_attempts += 1
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def reset_invalid_login_attempts(self, email: str) -> User | None:
        """Resets the number of invalid login attempts for a user to zero."""
        db_user: User = self.db.query(User).filter(User.email==email).first()
        if not db_user:
            return None
        db_user.invalid_login_attempts = 0
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def update_user_status(self, email: str, status: UserStatus) -> User | None:
        """Updates user status."""
        db_user: User = self.db.query(User).filter(User.email==email).first()
        if not db_user:
            return None
        db_user.status = status
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def verify_user(self, email: str) -> User | None:
        """Sets the user status to 'ACTIVE'."""
        db_user: User = self.db.query(User).filter(User.email==email).first()
        if not db_user:
            return None
        db_user.status = UserStatus.ACTIVE
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def update_last_login(self, email: str, last_login: datetime) -> User | None:
        """Updates last login to the current time."""
        db_user: User = self.db.query(User).filter(User.email==email).first()
        if not db_user:
            return None
        db_user.last_login = last_login
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    