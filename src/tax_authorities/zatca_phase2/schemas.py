from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional
from src.core.enums import TaxExemptionReasonCode, ZatcaPhase2Stage

class ZatcaPhase2CSIDBase(BaseModel):
    stage: ZatcaPhase2Stage
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
    organization_id: int
    branch_id: int
    model_config = ConfigDict(from_attributes=True)

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
        
class ZatcaPhase2ComplianceInvoiceResponse(BaseModel):
    status_code: int
    zatca_response: dict

class ZatcaSimplifiedInvoiceResponse(BaseModel):
    status_code: int
    zatca_response: dict

class ZatcaPhase2StandardInvoiceResponse(BaseModel):
    status_code: int
    zatca_response: dict
    invoice: Optional[str]

class ZatcaPhase2InvoiceLineMetadata(BaseModel):
    tax_exemption_reason_code: Optional[TaxExemptionReasonCode] = Field(None)
    tax_exemption_reason: Optional[str] = Field(None, min_length=1, max_length=200)
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2InvoiceMetadata(BaseModel):
    pih: Optional[str] = None 
    icv: Optional[int] = None
    signed_xml_base64: Optional[str] = None
    base64_qr_code: Optional[str] = None
    invoice_hash: Optional[str] = None
    stage: Optional[ZatcaPhase2Stage] = None
    status_code: Optional[int] = None
    response: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2BranchMetadataBase(BaseModel):
    stage: str
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

class ZatcaPhase2BranchMetadataCreate(ZatcaPhase2BranchMetadataBase):
    zatca_otp: str

class ZatcaPhase2BranchMetadataInDB(ZatcaPhase2BranchMetadataBase):
    organization_id: int
    branch_id: int
    pih: Optional[str] = None
    icv: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class ZatcaPhase2BranchMetadataOut(ZatcaPhase2BranchMetadataBase):
    model_config = ConfigDict(from_attributes=True)

