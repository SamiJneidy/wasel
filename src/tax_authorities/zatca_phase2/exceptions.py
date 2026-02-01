from fastapi import status
from src.core.exceptions.exceptions import BaseAppException


class ZatcaRequestFailedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "An error has occurred when sending the request to Zatca", 
        status_code: int = status.HTTP_408_REQUEST_TIMEOUT
    ):
        super().__init__(detail, status_code)

class ZatcaCSIDNotIssuedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "The CSID could not be issued by Zatca. Either the request in invalid or the OTP code is invalid.", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(detail, status_code)

class ZatcaInvoiceSigningException(BaseAppException):
    """Raised when the invoice could not be signed"""
    def __init__(self, detail: str | None = "An error has occurred when signing the invoice", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class ZatcaBranchDataNotFoundException(BaseAppException):
    def __init__(self, 
        detail: str | None = "Tax authority data for this branch was not found", 
        status_code: int = status.HTTP_404_NOT_FOUND,
    ):
        super().__init__(detail, status_code)
    
class ZatcaBranchDataUpdateNotAllowedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "Tax authority data for this branch is already created and cannot be updated", 
        status_code: int = status.HTTP_403_FORBIDDEN,
    ):
        super().__init__(detail, status_code)

class ZatcaBranchDataAlreadyCreatedException(BaseAppException):
    def __init__(self, 
        detail: str | None = "Tax authority data for this branch is already created", 
        status_code: int = status.HTTP_409_CONFLICT,
    ):
        super().__init__(detail, status_code)

