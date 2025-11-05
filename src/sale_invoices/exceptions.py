from fastapi import status
from src.core.exceptions import BaseAppException, IntegrityErrorException, raise_integrity_error

class InvoiceNotFoundException(BaseAppException):
    """Invoice not found"""
    def __init__(self, detail: str | None = "Invoice not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)


class InvoiceSigningError(BaseAppException):
    """Raised when the invoice could not be signed"""
    def __init__(self, detail: str | None = "An error has occurred when signing the invoice", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)
    

class InvoiceUpdateNotAllowed(BaseAppException):
    """Raised when attempting to update a locked invoice"""
    def __init__(self, detail: str | None = "Not allowed. Updates are permitted on quotations not on sale invoices.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class InvalidDocumentType(BaseAppException):
    """Raised when the document type does not match the endpoint"""
    def __init__(self, detail: str | None = "Invalid document type for the operation", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

    