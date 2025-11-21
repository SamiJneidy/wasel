from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ..repositories.otp_repo import OTPRepository
from ..services.otp_service import OTPService
from src.core.database import get_db

def get_otp_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> OTPRepository:
    """Returns otp repository dependency"""
    return OTPRepository(db)


def get_otp_service(
    otp_repo: Annotated[OTPRepository, Depends(get_otp_repository)],
) -> OTPService:
    
    """Returns otp service dependency"""
    return OTPService(otp_repo)
