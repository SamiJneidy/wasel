from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.branches.models import Branch
from src.core.database import Base
from src.core.models import AuditMixin, AuditTimeMixin
from src.core.enums import OrganizationTaxScheme

class Organization(Base, AuditTimeMixin):
    __tablename__ = "organizations"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(300))
    email = Column(String(200))
    country_code = Column(String(30))
    vat_number = Column(String(20), nullable=True)
    business_category = Column(String(100), nullable=True)
    tax_scheme = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    street = Column(String(300), nullable=True)
    building_number = Column(String(15), nullable=True)
    division = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    address = Column(String(400), nullable=True)
    