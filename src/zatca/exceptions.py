from fastapi import status
from src.core.exceptions.exceptions import BaseAppException


class ZatcaRequestFailedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "An error has occurred when sending the request to Zatca", 
        status_code: int = status.HTTP_408_REQUEST_TIMEOUT
    ):
        super().__init__(detail, status_code)

class CSIDNotIssuedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "The CSID could not be issued by Zatca. Either the request in invalid or the OTP code is invalid.", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(detail, status_code)

class InvoiceSigningException(BaseAppException):
    """Raised when the invoice could not be signed"""
    def __init__(self, detail: str | None = "An error has occurred when signing the invoice", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class ZatcaInvoiceNotAllowedException(BaseAppException):
    def __init__(self, detail: str | None = "Your tax scheme does not allow to send invoices to Zatca", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)


class InvoiceNotAcceptedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "The invoice was not accepted by zatca", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(detail, status_code)

class ZatcaBranchMetadataNotFoundException(BaseAppException):
    def __init__(self, 
        detail: str | None = "Metadata for this branch was not found", 
        status_code: int = status.HTTP_404_NOT_FOUND,
    ):
        super().__init__(detail, status_code)
    

class ZatcaBranchMetadataNotAllowedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "Your tax scheme does not allow branch metadata", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(detail, status_code)
