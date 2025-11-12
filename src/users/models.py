from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditTimeMixin
from src.core.enums import UserRole, UserStatus, UserType, Stage

class User(Base, AuditTimeMixin):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    phone = Column(String(20), nullable=True)
    last_login = Column(DateTime, nullable=True)
    invalid_login_attempts = Column(Integer, nullable=False, server_default=text("0"))
    type = Column(String(50), nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(UserStatus), nullable=False)
    is_completed = Column(Boolean, nullable=False)

    organization = relationship("Organization")

