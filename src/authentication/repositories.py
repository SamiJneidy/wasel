import secrets
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from .models import User, OTP
from src.core.enums import UserRole, UserStatus, OTPUsage, OTPStatus
from src.users.repositories import UserRepository

class AuthenticationRepository:
    def __init__(self, db: Session):
        self.db = db

    async def delete_user(self, email: str) -> None:
        """Deletes a user from the database. Note that this is NOT a soft delete, this will delete the user permanently from the database."""
        self.db.execute(delete(User).where(User.email==email))
        self.db.commit()

class OTPRepository:
    def __init__(self, db: Session):
        self.db = db

    async def revoke_otp_codes_for_user(self, email: str, usage: OTPUsage = None) -> None:
        """Revoke all generated OTP codes for a user with a specific usage (in case 'usage' was 'None', all OTP codes for the user will be revoked)."""
        stmt = delete(OTP).where(OTP.email==email, or_(usage is None, OTP.usage==usage))
        self.db.execute(stmt)
        self.db.commit()

    async def get_otp_by_code(self, code: str) -> OTP | None:
        """Returns an OTP model by code."""
        return self.db.query(OTP).filter(OTP.code==code).first()
    
    async def get_otp_by_email_and_usage(self, email: str, usage: OTPUsage) -> OTP | None:
        """Returns OTP code by email and usage."""
        return self.db.query(OTP).filter(OTP.email==email, OTP.usage==usage).first()

    async def get_code_count(self, code: str) -> int:
        """Returns the count of an OTP code. Used to maintain uniqueness when genrating new codes."""
        return self.db.execute(select(func.count()).select_from(OTP).where(OTP.code==code)).scalar()

    async def create_otp(self, data: dict) -> OTP:
        """Creates a new OTP code."""
        db_otp = OTP(**data)
        self.db.add(db_otp)
        self.db.commit()
        self.db.refresh(db_otp)
        return db_otp

    async def verify_otp(self, code: str) -> OTP | None:
        """Sets OTP code status to 'VERIFIED'."""
        db_otp: OTP = self.db.query(OTP).filter(OTP.code==code).first()
        if not db_otp:
            return None
        db_otp.status = OTPStatus.VERIFIED
        self.db.commit()
        self.db.refresh(db_otp)
        return db_otp
