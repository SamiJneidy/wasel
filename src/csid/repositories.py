from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from datetime import datetime
from .models import CSID
from src.core.enums import CSIDType
from src.sale_invoices.repositories import SaleInvoiceRepository

class CSIDRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_compliance_csid_by_id(self, id: int) -> CSID | None:
        return self.db.query(CSID).filter(CSID.id==id, CSID.type==CSIDType.COMPLIANCE).first()
    
    async def get_compliance_csid_by_user_id(self, user_id: int) -> CSID | None:
        return self.db.query(CSID).filter(CSID.user_id==user_id, CSID.type==CSIDType.COMPLIANCE).first()

    async def get_production_csid_by_id(self, id: int) -> CSID | None:
        return self.db.query(CSID).filter(CSID.id==id, CSID.type==CSIDType.PRODUCTION).first()
    
    async def get_production_csid_by_user_id(self, user_id: int) -> CSID | None:
        return self.db.query(CSID).filter(CSID.user_id==user_id, CSID.type==CSIDType.PRODUCTION).first()

    async def create(self, data: dict) -> CSID | None:
        csid = CSID(**data)
        self.db.add(csid)
        self.db.commit()
        self.db.refresh(csid)
        return csid

    async def update(self, id: int, data: dict) -> CSID | None:
        stmt = update(CSID).where(CSID.id==id).values(**data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get_compliance_csid_by_id(id)
    
    async def delete(self, id: int) -> CSID | None:
        csid = self.db.query(CSID).filter(CSID.id==id)
        if not csid:
            return None
        csid.delete()
        self.db.commit()
        return csid
