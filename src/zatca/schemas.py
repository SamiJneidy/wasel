from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional
from src.core.enums import TaxExemptionReasonCode, ZatcaStage

class ZatcaCSIDBase(BaseModel):
    stage: ZatcaStage
    request_id: str
    disposition_message: str
    binary_security_token: str
    secret: str
    private_key: str
    csr_base64: str
    certificate: str
    authorization: str

class ZatcaCSIDCreate(ZatcaCSIDBase):
    pass

class ZatcaCSIDInDB(ZatcaCSIDBase):
    id: int
    organization_id: int
    branch_id: int
    model_config = ConfigDict(from_attributes=True)

class ZatcaComplianceCSIDRequest(BaseModel):
    code: str = Field(..., pattern=r'^\d{6}$', description="The OTP code from Zatca portal")

class ZatcaCSIDOut(BaseModel):
    email: EmailStr
    
class ZatcaCSIDResponse(BaseModel):
    request_id: str
    disposition_message: str
    binary_security_token: str
    secret: str
    @field_validator('request_id', mode='before')
    def request_id_to_str(cls, value):
        return str(value)
        
class ZatcaComplianceInvoiceResponse(BaseModel):
    status_code: int
    zatca_response: dict

class ZatcaSimplifiedInvoiceResponse(BaseModel):
    status_code: int
    zatca_response: dict

class ZatcaStandardInvoiceResponse(BaseModel):
    status_code: int
    zatca_response: dict
    invoice: Optional[str]

class ZatcaInvoiceLineMetadata(BaseModel):
    tax_exemption_reason_code: Optional[TaxExemptionReasonCode] = Field(None)
    tax_exemption_reason: Optional[str] = Field(None, min_length=1, max_length=200)
    model_config = ConfigDict(from_attributes=True)

class ZatcaInvoiceMetadata(BaseModel):
    pih: Optional[str] = None 
    icv: Optional[int] = None
    signed_xml_base64: Optional[str] = None
    base64_qr_code: Optional[str] = None
    invoice_hash: Optional[str] = None
    stage: Optional[ZatcaStage] = None
    status_code: Optional[int] = None
    response: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ZatcaBranchMetadataBase(BaseModel):
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

class ZatcaBranchMetadataCreate(ZatcaBranchMetadataBase):
    zatca_otp: str

class ZatcaBranchMetadataInDB(ZatcaBranchMetadataBase):
    organization_id: int
    branch_id: int
    pih: Optional[str] = None
    icv: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class ZatcaBranchMetadataOut(ZatcaBranchMetadataBase):
    model_config = ConfigDict(from_attributes=True)

