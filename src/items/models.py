from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import PartyIdentificationScheme

class Item(Base, AuditMixin):
    __tablename__ = "items"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    name = Column(String(300), nullable=False)
    default_sale_price = Column(DECIMAL(scale=2), nullable=False)
    default_buy_price = Column(DECIMAL(scale=2), nullable=False)
    unit_code = Column(String(30), nullable=False)
    description = Column(String(400), nullable=True)