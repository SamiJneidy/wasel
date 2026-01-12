from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import PartyIdentificationScheme

class PointOfSale(Base, AuditMixin):
    __tablename__ = "points_of_sale"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    name = Column(String(300), nullable=False)