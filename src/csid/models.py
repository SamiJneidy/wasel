from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditTimeMixin
from src.core.enums import CSIDType

class CSID(Base, AuditTimeMixin):
    __tablename__ = "csids"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    type = Column(Enum(CSIDType), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    private_key = Column(String, nullable=False)
    csr_base64 = Column(String, nullable=False)
    request_id = Column(String, nullable=False)
    disposition_message = Column(String, nullable=False)
    binary_security_token = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    certificate = Column(String, nullable=False)
    authorization = Column(String, nullable=False)

    user = relationship("User", foreign_keys=[user_id], remote_side="User.id")
