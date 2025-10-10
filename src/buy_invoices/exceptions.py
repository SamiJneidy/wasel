from fastapi import status
from src.core.exceptions import BaseAppException, IntegrityErrorException, raise_integrity_error

class BuyInvoiceNotFoundException(BaseAppException):
    """Invoice not found"""
    def __init__(self, detail: str | None = "Invoice not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)

    