from fastapi import status
from src.core.exceptions.exceptions import BaseAppException


class ZatcaRequestFailedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "An error has occurred when sending the request to Zatca", 
        status_code: int = status.HTTP_408_REQUEST_TIMEOUT
    ):
        super().__init__(detail, status_code)


class BaseZatcaException(BaseAppException):
    def __init__(self, status_code: int, detail: str | None, zatca_response: dict | None):
        super().__init__(detail, status_code)
        self.zatca_response = zatca_response


class CSIDNotIssuedException(BaseZatcaException):
    def __init__(self, 
        detail: str | None = "The CSID could not be issued by Zatca. Either the request in invalid or the OTP code is invalid.", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
        zatca_response = None
    ):
        super().__init__(status_code, detail, zatca_response)


class InvoiceNotAcceptedException(BaseZatcaException):
    def __init__(self, 
        detail: str | None = "The invoice was not accepted by zatca", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
        zatca_response = None
    ):
        super().__init__(status_code, detail, zatca_response)

    
