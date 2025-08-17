from sqlalchemy.orm import Session
from sqlalchemy import exc, func, and_, or_, select, insert, update, delete, distinct
from datetime import datetime
from .models import Invoice, InvoiceCustomer, InvoiceLine
from src.users.schemas import UserOut
from src.core.enums import Stage, InvoiceType, InvoiceTypeCode

class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db


    async def get_last_invoice(self, user_id: int, stage: Stage) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.user_id==user_id, Invoice.stage==stage).order_by(Invoice.id).limit(1).first()

    async def get_invoice_count(self, user_id: int, stage: Stage) -> int:
        stmt = select(func.count(Invoice.id)).select_from(Invoice).where(and_(Invoice.user_id==user_id, Invoice.stage==stage))
        return self.db.execute(stmt).scalar()

    async def get_invoice_type_code_distinct_count(self, user_id: int, invoice_type: InvoiceType) -> int:
        stmt = select(func.count(distinct(Invoice.invoice_type_code))).select_from(Invoice).where(and_(Invoice.invoice_type==invoice_type, Invoice.user_id==user_id))
        return self.db.execute(stmt).scalar()

    async def get_invoice_customer(self, id: int) -> InvoiceCustomer | None:
        return self.db.query(InvoiceCustomer).filter(InvoiceCustomer.id==id).first()
    
    async def get_invoice_customer_by_invoice_id(self, invoice_id: int) -> InvoiceCustomer | None:
        return self.db.query(InvoiceCustomer).filter(InvoiceCustomer.invoice_id==invoice_id).first()

    async def create_invoice_customer(self, data: dict) -> InvoiceCustomer:
        customer = InvoiceCustomer(**data)
        self.db.add(customer)
        self.db.flush()
        return customer
        
    async def get_invoice_line(self, id: int) -> InvoiceLine | None:
        return self.db.query(InvoiceLine).filter(InvoiceLine.id==id).first()
    
    async def get_invoice_lines_by_invoice_id(self, invoice_id: int) -> list[InvoiceLine]:
        return self.db.query(InvoiceLine).filter(InvoiceLine.invoice_id==invoice_id).all()

    async def create_invoice_lines(self, data: list[dict]) -> None:
        self.db.bulk_insert_mappings(InvoiceLine, data)
        self.db.flush()
        
    async def get_invoice(self, user_id: int, id: int) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.user_id==user_id, Invoice.id==id).first()
    
    async def get_invoices_by_user_id(self, user_id: int, stage: Stage) -> list[Invoice] | None:
        return self.db.query(Invoice).filter(Invoice.user_id==user_id, Invoice.stage==stage).all()
    
    async def create_invoice(self, user_id: int, data: dict) -> Invoice | None:
        invoice = Invoice(**data)
        invoice.user_id = user_id
        invoice.created_by = user_id
        self.db.add(invoice)
        self.db.flush()
        return invoice      
    
    async def update_invoice(self, invoice_id: int, data: dict) -> None:
        stmt = update(Invoice).where(Invoice.id==invoice_id).values(**data)
        self.db.execute(stmt)

    async def count_invoices(self, user_id: int, stage: Stage) -> int:
        stmt = select(func.count()).select_from(Invoice).where(and_(Invoice.user_id==user_id, Invoice.stage==stage))
        return self.db.execute(stmt).scalar()
    