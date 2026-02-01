from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Literal, Optional
from src.core.enums import TaxExemptionReasonCode, ZatcaPhase2Stage, TaxAuthority, InvoiceTaxAuthorityStatus
from ..shared.schemas import (
    TaxAuthorityBase,
)

class ZatcaPhase2Discriminator(TaxAuthorityBase):
    tax_authority: Literal[TaxAuthority.ZATCA_PHASE2]


class ZatcaPhase2CSIDBase(BaseModel):
    request_id: str
    disposition_message: str
    binary_security_token: str
    secret: str
    private_key: str
    csr_base64: str
    certificate: str
    authorization: str

class ZatcaPhase2CSIDCreate(ZatcaPhase2CSIDBase):
    pass

class ZatcaPhase2CSIDInDB(ZatcaPhase2CSIDBase):
    id: int
    stage: ZatcaPhase2Stage
    organization_id: int
    branch_id: int
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2InvoiceResponse(ZatcaPhase2Discriminator):
    status: InvoiceTaxAuthorityStatus
    status_code: int
    response: dict
    signed_xml_base64: Optional[str] = None

class ZatcaPhase2InvoiceDataBase(ZatcaPhase2Discriminator):
    status: InvoiceTaxAuthorityStatus
    status_code: int
    response: dict
    signed_xml_base64: Optional[str] = None
    pih: Optional[str] = None 
    icv: Optional[int] = None
    base64_qr_code: Optional[str] = None
    invoice_hash: Optional[str] = None
    stage: Optional[ZatcaPhase2Stage] = None

class ZatcaPhase2InvoiceDataCreate(ZatcaPhase2InvoiceDataBase):
    pass

class ZatcaPhase2InvoiceDataOut(ZatcaPhase2InvoiceDataBase):
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2InvoiceLineDataCreate(ZatcaPhase2Discriminator):
    tax_exemption_reason_code: Optional[TaxExemptionReasonCode] = Field(None)
    tax_exemption_reason: Optional[str] = Field(None, min_length=1, max_length=200)

class ZatcaPhase2InvoiceLineDataOut(ZatcaPhase2Discriminator):
    tax_exemption_reason_code: Optional[TaxExemptionReasonCode] = Field(None)
    tax_exemption_reason: Optional[str] = Field(None, min_length=1, max_length=200)
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2BranchDataBase(ZatcaPhase2Discriminator):
    country_code: str
    registration_name: str
    common_name: str
    organization_unit_name: str
    organization_name: str
    vat_number: str
    invoicing_type: str
    address: str
    business_category: str
    street: str
    building_number: str
    division: str
    city: str
    postal_code: str
    party_identification_scheme: str
    party_identification_value: str

class ZatcaPhase2BranchDataCreate(ZatcaPhase2BranchDataBase):
    model_config = ConfigDict(from_attributes=True)


class ZatcaPhase2BranchDataUpdate(ZatcaPhase2BranchDataBase):
    model_config = ConfigDict(from_attributes=True)


class ZatcaPhase2BranchDataInDB(ZatcaPhase2BranchDataBase):
    stage: str
    organization_id: int
    branch_id: int
    pih: Optional[str] = None
    icv: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2BranchDataOut(ZatcaPhase2BranchDataBase):
    stage: ZatcaPhase2Stage
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2BranchDataComplete(ZatcaPhase2Discriminator):
    otp: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$', description="The OTP code from Zatca portal")

class ZatcaPhase2ComplianceCSIDRequest(BaseModel):
    code: str = Field(..., pattern=r'^\d{6}$', description="The OTP code from Zatca portal")

class ZatcaPhase2CSIDOut(BaseModel):
    email: EmailStr
    
class ZatcaPhase2CSIDResponse(BaseModel):
    request_id: str
    disposition_message: str
    binary_security_token: str
    secret: str
    @field_validator('request_id', mode='before')
    def request_id_to_str(cls, value):
        return str(value)