from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import TaxScheme

class ZatcaInfo(Base, AuditMixin):
    __tablename__ = "zatca_info"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'))
    country_code = Column(String(5), nullable=False)
    registration_name = Column(String(250), nullable=True)
    common_name = Column(String(250), nullable=True)
    organization_unit_name = Column(String(250), nullable=True)
    organization_name = Column(String(250), nullable=True)
    vat_number = Column(String(20), nullable=True)
    invoicing_type = Column(String(5), nullable=True)
    address = Column(String(400), nullable=True)
    business_category = Column(String(100), nullable=True)
    street = Column(String(300), nullable=True)
    building_number = Column(String(15), nullable=True)
    division = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    party_identification_scheme = Column(String(10), nullable=True)
    party_identification_value = Column(String(30), nullable=True)
    