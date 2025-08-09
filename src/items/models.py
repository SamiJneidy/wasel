from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import PartyIdentificationScheme

class Item(Base, AuditMixin):
    __tablename__ = "items"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(300), nullable=False)
    price = Column(DECIMAL(scale=2), nullable=False)
    unit_code = Column(String(30), nullable=False)
    