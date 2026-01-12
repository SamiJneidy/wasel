from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import PartyIdentificationScheme

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Numeric
from sqlalchemy.orm import relationship

class Project(Base, AuditMixin):
    __tablename__ = "projects"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(String, nullable=True)
    status = Column(String(30), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget_amount = Column(Numeric(14, 2), nullable=True)

    customer = relationship("Customer", lazy="selectin", foreign_keys=[customer_id])