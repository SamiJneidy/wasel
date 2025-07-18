from datetime import datetime, timedelta, timezone
from src.core.enums import OTPStatus, OTPUsage
from src.core.config import settings
from ..repositories import OTPRepository
from ..utils import generate_random_code
from ..schemas import (
    OTPCreate,
    OTPOut, 
)
from ..exceptions import (
    InvalidOTPException,
)


class OTPService:
    def __init__(self, otp_repo: OTPRepository) -> None:
        self.otp_repo = otp_repo

    async def get_otp_by_code(self, code: str) -> OTPOut:
        """Returns OTP by code."""
        db_otp = await self.otp_repo.get_otp_by_code(code)
        if not db_otp:
            raise InvalidOTPException()
        return OTPOut.model_validate(db_otp)


    async def get_otp_by_email_and_usage(self, email: str, usage: OTPUsage) -> OTPOut:
        """Returns OTP by email and usage."""
        db_otp = await self.otp_repo.get_otp_by_email_and_usage(email, usage)
        if not db_otp:
            raise InvalidOTPException()
        return OTPOut.model_validate(db_otp)


    async def generate_otp_code(self) -> str:
        """Generates a unique OTP code."""
        
        while True:    
            code: str = generate_random_code()
            code_count: int = await self.otp_repo.get_code_count(code)
            if code_count == 0:
                break
        
        return code
    

    async def create_otp(self, data: OTPCreate) -> OTPOut:
        """Creates an OTP code in the database."""
        
        await self.otp_repo.revoke_otp_codes_for_user(data.email, data.usage)
        
        code = await self.generate_otp_code()
        data_dict = data.model_dump()
        data_dict.update({"code": code, "status": OTPStatus.PENDING})
        
        db_otp = await self.otp_repo.create_otp(data_dict)
        
        return OTPOut.model_validate(db_otp)


    async def otp_is_expired(self, code: str) -> bool:
        """Checks if an OTP code is expired or not."""
        db_otp = await self.otp_repo.get_otp_by_code(code)
        if db_otp.expires_at < datetime.utcnow() or db_otp.status == OTPStatus.EXPIRED:
            return True
        return False


    async def verify_otp(self, code: str) -> None:
        """Verifies OTP code. Raises InvalidOTPException if the otp is expired, used before or not found."""
        
        db_otp = await self.otp_repo.get_otp_by_code(code)
        if db_otp is None:
            raise InvalidOTPException()
        if await self.otp_is_expired(code):
            raise InvalidOTPException()
        if db_otp.status != OTPStatus.PENDING:
            raise InvalidOTPException()
        
        db_otp = await self.otp_repo.verify_otp(code)
        return None


    async def revoke_otp_codes_for_user(self, email: str, usage: OTPUsage) -> None:
        await self.otp_repo.revoke_otp_codes_for_user(email, usage)
        return None
    