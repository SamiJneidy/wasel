from fastapi import status
from src.core.exceptions import BaseAppException, IntegrityErrorException, raise_integrity_error

class BuyInvoiceNotFoundException(BaseAppException):
    """Invoice not found"""
    def __init__(self, detail: str | None = "Invoice not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)

class BuyInvoiceDeleteNotAllowedException(BaseAppException):
    """Invoice delete not allowed"""
    def __init__(self, detail: str | None = "Invoice delete not allowed", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class BuyInvoiceValidationException(BaseAppException):
    """Raised when invoice business rules are violated"""
    def __init__(self, detail: str | None = "Invoice validation failed", status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        super().__init__(detail, status_code)