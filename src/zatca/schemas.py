from pydantic import BaseModel, Field, field_validator
from typing import Optional


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
