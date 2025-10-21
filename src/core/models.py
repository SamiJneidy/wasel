from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from src.core.consts import KSA_TZ
from datetime import datetime

def ksa_now():
    return datetime.now(KSA_TZ)

class AuditByMixin:
    """Adds created_by and updated_by columns to a model."""
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)

class AuditTimeMixin:
    """Adds created_at and updated_at columns to a model."""
    created_at = Column(DateTime(timezone=True), default=ksa_now, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=ksa_now, onupdate=ksa_now, nullable=True)

class AddressMixin:
    """Adds address fields to a model."""
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)

class AuditMixin(AuditTimeMixin, AuditByMixin):
    """Adds created_at, created_by, updated_at and updated_by to a model."""
    pass
