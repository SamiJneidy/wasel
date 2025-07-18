from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import BaseModel
from src.core.enums import UserRole, UserStatus, OTPUsage, OTPStatus
from src.users.models import User

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    email = Column(String(), nullable=False, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    usage = Column(SQLEnum(OTPUsage), nullable=False)
    status = Column(SQLEnum(OTPStatus), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    