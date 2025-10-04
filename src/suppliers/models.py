from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import PartyIdentificationScheme

class Supplier(Base, AuditMixin):
    __tablename__ = "suppliers"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    registration_name = Column(String(250), nullable=True)
    vat_number = Column(String(20), nullable=True)
    country_code = Column(String(5), nullable=True, server_default="SA")
    street = Column(String(300), nullable=True)
    building_number = Column(String(15), nullable=True)
    division = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    party_identification_scheme = Column(String(10), nullable=True)
    party_identification_value = Column(String(30), nullable=True)
    phone = Column(String(20), nullable=True)
    bank_account = Column(String(100), nullable=True)
    website = Column(String(100), nullable=True)
    notes = Column(String(1000), nullable=True)
    