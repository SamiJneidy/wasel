from sqlalchemy import BOOLEAN, Column, Integer, String, UUID, Date, Text, DECIMAL, DateTime, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxExemptionReasonCode, Stage


class SaleInvoice(Base, AuditMixin):
    __tablename__ = "sale_invoices"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    invoice_type = Column(Enum(InvoiceType), nullable=False)
    invoice_type_code = Column(Enum(InvoiceTypeCode), nullable=False)
    issue_date = Column(Date, nullable=False)
    issue_time = Column(String(15), nullable=False)
    document_currency_code = Column(String(5), nullable=False, server_default="SAR")
    actual_delivery_date = Column(Date, nullable=True)
    payment_means_code = Column(Enum(PaymentMeansCode), nullable=False)
    original_invoice_id = Column(Integer, ForeignKey('sale_invoices.id'), nullable=True)
    instruction_note = Column(String(4000), nullable=True)
    note = Column(String(4000), nullable=True)
    line_extension_amount = Column(DECIMAL(scale=2), nullable=False)
    discount_amount = Column(DECIMAL(scale=2), nullable=False)
    prices_include_tax = Column(BOOLEAN, nullable=False)
    taxable_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_inclusive_amount = Column(DECIMAL(scale=2), nullable=False)
    payable_amount = Column(DECIMAL(scale=2), nullable=False)
    signed_xml_base64 = Column(Text, nullable=True)
    invoice_hash = Column(Text, nullable=True)
    uuid = Column(UUID, nullable=True)
    icv = Column(Integer, nullable=False)
    pih = Column(Text, nullable=False)
    base64_qr_code = Column(Text, nullable=True)
    stage = Column(Enum(Stage), nullable=True)
    zatca_response = Column(Text, nullable=True)
    status_code = Column(String(5), nullable=True)
    user = relationship("User", foreign_keys=[user_id], remote_side="User.id")


class SaleInvoiceLine(Base):
    __tablename__ = "sale_invoices_lines"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey('sale_invoices.id', ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id', ondelete="RESTRICT"), nullable=False)
    item_price = Column(DECIMAL(scale=2), nullable=False)
    price_includes_tax = Column(BOOLEAN)
    price_discount = Column(DECIMAL(scale=2), nullable=False)
    quantity = Column(DECIMAL(scale=6), nullable=False)
    discount_amount = Column(DECIMAL(scale=2), nullable=False)
    line_extension_amount = Column(DECIMAL(scale=2), nullable=False)
    tax_amount = Column(DECIMAL(scale=2), nullable=False)
    rounding_amount = Column(DECIMAL(scale=2), nullable=False)
    classified_tax_category = Column(String(5), nullable=False)
    tax_rate = Column(DECIMAL(scale=2), nullable=False)    
    tax_exemption_reason_code = Column(Enum(TaxExemptionReasonCode), nullable=True)
    tax_exemption_reason = Column(String(200), nullable=True)
    