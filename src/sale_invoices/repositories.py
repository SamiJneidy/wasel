from sqlalchemy.orm import Session
from sqlalchemy import exc, func, and_, or_, select, insert, update, delete, distinct
from datetime import datetime

from sqlalchemy.sql.functions import user
from .models import SaleInvoice, SaleInvoiceLine
from src.users.schemas import UserOut
from src.core.enums import Stage, InvoiceType, InvoiceTypeCode

class SaleInvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_last_invoice(self, user_id: int, stage: Stage, filters: dict = {}) -> SaleInvoice | None:
        query = self.db.query(SaleInvoice).filter(SaleInvoice.user_id==user_id, SaleInvoice.stage==stage)
        for column, value in filters.items():
            c = getattr(SaleInvoice, column, None)
            if c is not None:
                query = query.filter(c == value)
        return query.order_by(SaleInvoice.id).limit(1).first()

    async def get_invoice_count(self, user_id: int, stage: Stage) -> int:
        stmt = select(func.count(SaleInvoice.id)).select_from(SaleInvoice).where(and_(SaleInvoice.user_id==user_id, SaleInvoice.stage==stage))
        return self.db.execute(stmt).scalar()

    async def get_invoice_type_code_distinct_count(self, user_id: int, invoice_type: InvoiceType) -> int:
        stmt = select(func.count(distinct(SaleInvoice.invoice_type_code))).select_from(SaleInvoice).where(and_(SaleInvoice.invoice_type==invoice_type, SaleInvoice.user_id==user_id))
        return self.db.execute(stmt).scalar()

    async def get_invoice_line(self, id: int) -> SaleInvoiceLine | None:
        return self.db.query(SaleInvoiceLine).filter(SaleInvoiceLine.id==id).first()
    
    async def get_invoice_lines_by_invoice_id(self, invoice_id: int) -> list[SaleInvoiceLine]:
        return self.db.query(SaleInvoiceLine).filter(SaleInvoiceLine.invoice_id==invoice_id).all()
    
    async def get_invoice(self, user_id: int, id: int) -> SaleInvoice | None:
        return self.db.query(SaleInvoice).filter(SaleInvoice.user_id==user_id, SaleInvoice.id==id).first()
    
    async def get_invoices_by_user_id(self, user_id: int, stage: Stage, skip: int = None, limit: int = None, filters: dict = {}) -> tuple[int, list[SaleInvoice]]:
        query = self.db.query(SaleInvoice).filter(SaleInvoice.user_id==user_id, SaleInvoice.stage==stage)
        # simple equality filters
        for k, v in filters.items():
            column = getattr(SaleInvoice, k, None)
            if column is not None:
                query = query.filter(column == v)
        # date range filters
        if filters.get("issue_date_range_from") is not None:
            query = query.filter(SaleInvoice.issue_date >= filters["issue_date_range_from"])
        if filters.get("issue_date_range_to") is not None:
            query = query.filter(SaleInvoice.issue_date <= filters["issue_date_range_to"])

        total_rows = query.count()
        # pagination parameters    
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        return total_rows, query.all()
    
    async def create_invoice_lines(self, data: list[dict]) -> None:
        self.db.bulk_insert_mappings(SaleInvoiceLine, data)
        self.db.flush()
        
    async def create_invoice(self, user_id: int, data: dict) -> SaleInvoice | None:
        invoice = SaleInvoice(**data)
        invoice.user_id = user_id
        invoice.created_by = user_id
        self.db.add(invoice)
        self.db.flush()
        return invoice      
    
    async def update_invoice(self, invoice_id: int, data: dict) -> None:
        stmt = update(SaleInvoice).where(SaleInvoice.id==invoice_id).values(**data)
        self.db.execute(stmt)

    async def count_invoices(self, user_id: int, stage: Stage) -> int:
        stmt = select(func.count()).select_from(SaleInvoice).where(and_(SaleInvoice.user_id==user_id, SaleInvoice.stage==stage))
        return self.db.execute(stmt).scalar()
