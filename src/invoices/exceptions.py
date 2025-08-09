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
    
class SwitchToProductionForbiddenException(BaseAppException):
    """Raised when trying to switch to production where the user hasn't uploaded the necessary compliance invoices"""
    def __init__(self, detail: str | None = "You are not allowed to switch to production at the moment because you haven't finished uploading the compliance invoices. You have to upload one invoice of each type of your invoicing type with its credit and debit notes (at least one invoice, credit note and debit note for each type of your invoicing type).", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)
    