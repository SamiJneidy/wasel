from fastapi import status
from src.core.exceptions.exceptions import BaseAppException


class IncorrectTaxAuthorityException(BaseAppException):
    def __init__(self, 
        detail: str | None = "Incorrect tax authority for this operation", 
        status_code: int = status.HTTP_403_FORBIDDEN
    ):
        super().__init__(detail, status_code)

class InvoiceNotAcceptedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "The invoice was not accepted by the tax authority", 
        tax_authority_response: dict | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.tax_authority_response = tax_authority_response
        super().__init__(detail, status_code)