from sqlalchemy import BOOLEAN, Column, Integer, String, UUID, Date, Text, DECIMAL, DateTime, ForeignKey, Enum, func, text, TIME
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxExemptionReasonCode, ZatcaPhase2Stage, DocumentType


class SaleInvoice(Base, AuditMixin):
    __tablename__ = "sale_invoices"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    year = Column(Integer, nullable=True, index=True)
    seq_number = Column(Integer, nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    invoice_number = Column(String(50), index=True, nullable=True)
    document_type = Column(Enum(DocumentType, native_enum=False), nullable=True)
    invoice_type = Column(Enum(InvoiceType), nullable=False)
    invoice_type_code = Column(Enum(InvoiceTypeCode), nullable=False)
    issue_date = Column(Date, nullable=False)
    issue_time = Column(TIME, nullable=False)
    document_currency_code = Column(String(5), nullable=False, server_default="SAR")
    actual_delivery_date = Column(Date, nullable=True)
    payment_means_code = Column(Enum(PaymentMeansCode), nullable=False)
    original_invoice_id = Column(String(30), nullable=True)
    instruction_note = Column(String(4000), nullable=True)
    note = Column(String(4000), nullable=True)
    line_extension_amount = Column(DECIMAL(scale=2), nullable=False)
    discount_amount = Column(DECIMAL(scale=2), nullable=False)
    prices_include_tax = Column(BOOLEAN, nullable=True)
    taxable_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_inclusive_amount = Column(DECIMAL(scale=2), nullable=False)
    payable_amount = Column(DECIMAL(scale=2), nullable=False)
    uuid = Column(UUID, nullable=True)
    is_locked = Column(BOOLEAN, nullable=True)
    completed_tax_integration = Column(BOOLEAN, nullable=True)


class SaleInvoiceLine(Base):
    __tablename__ = "sale_invoices_lines"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey('sale_invoices.id', ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id', ondelete="RESTRICT"), nullable=False)
    item_price = Column(DECIMAL(scale=2), nullable=False)
    price_includes_tax = Column(BOOLEAN, nullable=True)
    price_discount = Column(DECIMAL(scale=2), nullable=False)
    quantity = Column(DECIMAL(scale=6), nullable=False)
    discount_amount = Column(DECIMAL(scale=2), nullable=False)
    line_extension_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_amount = Column(DECIMAL(scale=2), nullable=False)
    rounding_amount = Column(DECIMAL(scale=2), nullable=False)
    classified_tax_category = Column(String(5), nullable=False)
    tax_rate = Column(DECIMAL(scale=2), nullable=False)    
    