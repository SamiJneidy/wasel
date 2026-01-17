from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditTimeMixin, AuditMixin
from src.core.enums import UserRole, UserStatus, UserType, ZatcaPhase2Stage

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    description = Column(String, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('resource', 'action', name='unique_permission_resource_action'),
    )

class UserPermission(Base, AuditMixin):
    __tablename__ = "user_permissions"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)
    is_allowed = Column(Boolean, nullable=False)

    permission = relationship("Permission", foreign_keys=[permission_id], lazy="joined")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id', name='unique_user_permission'),
    )
