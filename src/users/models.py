from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditTimeMixin
from src.core.enums import UserRole, UserStatus, OTPUsage, OTPStatus

class User(Base, AuditTimeMixin):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=True)
    invalid_login_attempts = Column(Integer, nullable=False, server_default=text("0"))
    role = Column(SQLEnum(UserRole), nullable=False)
    status = Column(SQLEnum(UserStatus), nullable=False)
    phone = Column(String(20), nullable=True)
    is_completed = Column(Boolean, nullable=True)
    
    registraion_name = Column(String(250), nullable=True)
    common_name = Column(String(250), nullable=True)
    organization_unit_name = Column(String(250), nullable=True)
    organization_name = Column(String(250), nullable=True)
    vat_number = Column(String(20), nullable=True)
    invoicing_type = Column(String(5), nullable=True)
    address = Column(String(400), nullable=True)
    business_category = Column(String(100), nullable=True)
    country_code = Column(String(5), nullable=True, server_default="SA")
    street = Column(String(300), nullable=True)
    building_number = Column(String(15), nullable=True)
    division = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    party_identification_scheme = Column(String(10), nullable=True)
    party_identification_value = Column(String(30), nullable=True)
    