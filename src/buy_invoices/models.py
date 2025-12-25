from sqlalchemy import BOOLEAN, Column, Integer, String, UUID, Date, Text, DECIMAL, DateTime, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxExemptionReasonCode, ZatcaPhase2Stage


class BuyInvoice(Base, AuditMixin):
    __tablename__ = "buy_invoices"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    seq_number = Column(Integer, nullable=True)
    invoice_number = Column(String(100), nullable=True)
    invoice_type_code = Column(Enum(InvoiceTypeCode), nullable=False)
    issue_date = Column(Date, nullable=False)
    document_currency_code = Column(String(5), nullable=False, server_default="SAR")
    actual_delivery_date = Column(Date, nullable=True)
    payment_means_code = Column(Enum(PaymentMeansCode), nullable=False)
    original_invoice_id = Column(Integer, ForeignKey('buy_invoices.id'), nullable=True)
    instruction_note = Column(String(4000), nullable=True)
    note = Column(String(4000), nullable=True)
    line_extension_amount = Column(DECIMAL(scale=2), nullable=False)
    discount_amount = Column(DECIMAL(scale=2), nullable=False)
    taxable_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_inclusive_amount = Column(DECIMAL(scale=2), nullable=False)
    uuid = Column(UUID, nullable=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete="RESTRICT"), nullable=True)


class BuyInvoiceLine(Base):
    __tablename__ = "buy_invoices_lines"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey('buy_invoices.id', ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id', ondelete="RESTRICT"), nullable=False)
    item_price = Column(DECIMAL(scale=2), nullable=False)
    price_discount = Column(DECIMAL(scale=2), nullable=True)
    price_includes_tax = Column(BOOLEAN)
    quantity = Column(DECIMAL(scale=6), nullable=False)
    discount_amount = Column(DECIMAL(scale=2), nullable=False)
    line_extension_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_amount = Column(DECIMAL(scale=2), nullable=False)
    rounding_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_rate = Column(DECIMAL(scale=2), nullable=False)    
    classified_tax_category = Column(String(5), nullable=False)
    description = Column(String(200), nullable=True)