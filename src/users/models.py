from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditTimeMixin
from src.core.enums import UserRole, UserStatus, UserType, ZatcaPhase2Stage

class User(Base, AuditTimeMixin):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    default_branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String, nullable=True)
    phone = Column(String(20), nullable=True)
    last_login = Column(DateTime, nullable=True)
    invalid_login_attempts = Column(Integer, nullable=False, server_default=text("0"))
    type = Column(String(50), nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="RESTRICT"), nullable=True)
    status = Column(Enum(UserStatus), nullable=False)
    is_completed = Column(Boolean, nullable=False)
    is_super_admin = Column(Boolean, nullable=False, server_default=text("false"))
    organization = relationship("Organization", lazy="selectin", foreign_keys=[organization_id])
    default_branch = relationship("Branch", lazy="selectin", foreign_keys=[default_branch_id])
    role = relationship("Role", lazy="selectin", foreign_keys=[role_id])

