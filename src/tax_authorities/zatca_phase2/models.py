from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, ForeignKey, Enum, func, text, JSON
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.core.models import AuditMixin
from src.core.enums import TaxAuthority, ZatcaPhase2Stage, TaxExemptionReasonCode

class ZatcaPhase2SaleInvoiceData(Base, AuditMixin):
    __tablename__ = "zatca_phase2_sale_invoice_data"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    tax_authority = Column(String(50), nullable=True, default=TaxAuthority.ZATCA_PHASE2.value)
    invoice_id = Column(Integer, ForeignKey('sale_invoices.id', ondelete="CASCADE"))
    icv = Column(Integer, nullable=True)
    signed_xml_base64 = Column(Text, nullable=True)
    invoice_hash = Column(Text, nullable=True)
    pih = Column(Text, nullable=True)
    base64_qr_code = Column(Text, nullable=True)
    stage = Column(String(50), nullable=True)
    response = Column(JSON, nullable=True)
    status = Column(String(50), nullable=True)
    status_code = Column(Integer, nullable=True)

class ZatcaPhase2SaleInvoiceLineData(Base, AuditMixin):
    __tablename__ = "zatca_phase2_sale_invoice_lines_data"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    tax_authority = Column(String(50), nullable=True, default=TaxAuthority.ZATCA_PHASE2.value)
    invoice_id = Column(Integer, ForeignKey('sale_invoices.id', ondelete="CASCADE"))
    invoice_line_id = Column(Integer, ForeignKey('sale_invoices_lines.id', ondelete="CASCADE"))
    tax_exemption_reason_code = Column(String(100), nullable=True)
    tax_exemption_reason = Column(String(200), nullable=True)

class ZatcaPhase2BranchData(Base, AuditMixin):
    __tablename__ = "zatca_phase2_branches_data"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    tax_authority = Column(String(50), nullable=True, default=TaxAuthority.ZATCA_PHASE2.value)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'))
    stage = Column(String, nullable=True)
    icv = Column(Integer, nullable=True)
    pih = Column(Text, nullable=True)
    country_code = Column(String(50), nullable=False)
    registration_name = Column(String(250), nullable=True)
    common_name = Column(String(250), nullable=True)
    organization_unit_name = Column(String(250), nullable=True)
    organization_name = Column(String(250), nullable=True)
    vat_number = Column(String(20), nullable=True)
    invoicing_type = Column(String(50), nullable=True)
    address = Column(String(400), nullable=True)
    business_category = Column(String(100), nullable=True)
    street = Column(String(300), nullable=True)
    building_number = Column(String(15), nullable=True)
    division = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    party_identification_scheme = Column(String(10), nullable=True)
    party_identification_value = Column(String(30), nullable=True)
    
class ZatcaPhase2CSID(Base, AuditMixin):
    __tablename__ = "zatca_phase2_csids"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    stage = Column(String(50), nullable=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'))
    private_key = Column(String, nullable=False)
    csr_base64 = Column(String, nullable=False)
    request_id = Column(String, nullable=False)
    disposition_message = Column(String, nullable=False)
    binary_security_token = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    certificate = Column(String, nullable=False)
    authorization = Column(String, nullable=False)