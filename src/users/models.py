from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditTimeMixin
from src.core.enums import UserRole, UserStatus, Stage

class User(Base, AuditTimeMixin):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=True)
    invalid_login_attempts = Column(Integer, nullable=False, server_default=text("0"))
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(UserStatus), nullable=False)
    phone = Column(String(20), nullable=True)
    is_completed = Column(Boolean, nullable=False)
