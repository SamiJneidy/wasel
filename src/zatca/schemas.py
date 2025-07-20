from pydantic import BaseModel, Field, field_validator


class ZatcaCSIDResponse(BaseModel):
    request_id: str
    disposition_message: str
    binary_security_token: str
    secret: str
    
    @field_validator('request_id', mode='before')
    def request_id_to_str(cls, value):
        return str(value)
        