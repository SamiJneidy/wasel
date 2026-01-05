from fastapi import status
from src.core.exceptions import BaseAppException, IntegrityErrorException, raise_integrity_error

class InvoiceNotFoundException(BaseAppException):
    """Invoice not found"""
    def __init__(self, detail: str | None = "Invoice not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)

class InvoiceUpdateNotAllowed(BaseAppException):
    """Raised when attempting to update a locked invoice"""
    def __init__(self, detail: str | None = "Not allowed. Update is permitted on unlocked invoices.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class InvoiceDeleteNotAllowed(BaseAppException):
    """Raised when attempting to delete a locked invoice"""
    def __init__(self, detail: str | None = "Not allowed. Delete is permitted on unlocked invoices.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class InvoiceSendNotAllowed(BaseAppException):
    """Raised when attempting to send an invoice"""
    def __init__(self, detail: str | None = "Invoice can not be sent", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class InvalidDocumentType(BaseAppException):
    """Raised when the document type does not match the endpoint"""
    def __init__(self, detail: str | None = "Invalid document type for the operation", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

