from fastapi import status
from src.core.exceptions import BaseAppException


class ZatcaRequestFailedException(BaseAppException):
    def __init__(self, detail: str = "An error has occurred when sending the request to Zatca", status_code: int = status.HTTP_408_REQUEST_TIMEOUT):
        super().__init__(detail, status_code)


class BaseZatcaException(Exception):
    def __init__(self, status_code: int, detail: str, zatca_response: dict | None):
        self.status_code = status_code
        self.detail = detail
        self.zatca_response = zatca_response


class ComplianceCSIDNotIssuedException(BaseZatcaException):
    def __init__(self, 
        detail: str = "The CSID could not be issued by Zatca. Either the request in invalid or the OTP code is invalid.", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
        zatca_response = None
    ):
        super().__init__(status_code, detail, zatca_response)


