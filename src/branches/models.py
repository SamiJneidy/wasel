from sqlalchemy import BOOLEAN, Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin, AuditTimeMixin
from src.core.enums import TaxScheme

class Branch(Base, AuditMixin):
    __tablename__ = "branches"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    is_main_branch = Column(BOOLEAN)
    name = Column(String(300))
    phone = Column(String(50), nullable=True)
    street = Column(String(300), nullable=True)
    building_number = Column(String(15), nullable=True)
    division = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    address = Column(String(400), nullable=True)
    