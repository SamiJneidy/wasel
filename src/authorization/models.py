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

class Role(Base, AuditMixin):
    __tablename__ = "roles"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    is_immutable = Column(Boolean, nullable=False, server_default=text("false"))
    
class RolePermission(Base, AuditMixin):
    __tablename__ = "role_permissions"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)
    is_allowed = Column(Boolean, nullable=False)

    permission = relationship("Permission", foreign_keys=[permission_id], lazy="joined")
    
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='unique_role_permission'),
    )

class UserBranch(Base):
    __tablename__ = "user_branches"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    branch = relationship("Branch", lazy="selectin", foreign_keys=[branch_id])
    __table_args = (
        UniqueConstraint("organization_id", "user_id", "branch_id", name="unique_organization_branch_user")
    )
