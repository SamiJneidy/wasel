from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, select, insert, update, delete
from .models import User, OTP
from src.core.enums import OTPUsage, OTPStatus

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_user(self, email: str) -> None:
        """Deletes a user from the database. Note that this is NOT a soft delete, this will delete the user permanently from the database."""
        stmt = delete(User).where(User.email==email)
        await self.db.execute(stmt)
        await self.db.flush()
        return None


class OTPRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def revoke_otp_codes_for_user(self, email: str, usage: OTPUsage = None) -> None:
        """Revoke all generated OTP codes for a user with a specific usage (in case 'usage' was 'None', all OTP codes for the user will be revoked)."""
        stmt = delete(OTP).where(OTP.email==email, or_(usage is None, OTP.usage==usage))
        await self.db.execute(stmt)
        await self.db.flush()
        return None

    async def get_otp_by_code(self, code: str) -> Optional[OTP]:
        """Returns an OTP model by code."""
        stmt = select(OTP).where(OTP.code==code)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_otp_by_email_and_usage(self, email: str, usage: OTPUsage) -> OTP | None:
        """Returns OTP code by email and usage."""
        stmt = select(OTP).where(OTP.email==email, OTP.usage==usage)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_code_count(self, code: str) -> int:
        """Returns the count of an OTP code. Used to maintain uniqueness when genrating new codes."""
        stmt = select(func.count()).select_from(OTP).where(OTP.code==code)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_otp(self, data: dict) -> OTP:
        """Creates a new OTP code."""
        otp = OTP(**data)
        self.db.add(otp)
        await self.db.flush()
        await self.db.refresh(otp)
        return otp

    async def verify_otp(self, code: str) -> OTP | None:
        """Sets OTP code status to 'VERIFIED'."""
        stmt = select(OTP).where(OTP.code==code)
        result = await self.db.execute(stmt)
        otp = result.scalars().first()
        if not otp:
            return None
        otp.status = OTPStatus.VERIFIED
        await self.db.flush()
        await self.db.refresh(otp)
        return otp

    async def delete_otp(self, code: str) -> OTP | None:
        stmt = select(OTP).where(OTP.code==code)
        result = await self.db.execute(stmt)
        otp = result.scalars().first()
        if not otp:
            return None
        stmt = delete(OTP).where(OTP.code==code)
        await self.db.execute(stmt)
        await self.db.flush()
        return otp
        