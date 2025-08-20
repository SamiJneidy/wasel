from fastapi import status
from src.core.exceptions.exceptions import BaseAppException
from src.users.exceptions import UserNotCompleteException

class RequestNotSentException(BaseAppException):
    """Raised when the request could not be sent."""
    def __init__(self, detail: str | None = "Could not send the request", status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE):
        super().__init__(detail, status_code)

class SwitchToProductionForbiddenException(BaseAppException):
    """Raised when trying to switch to production where the user hasn't uploaded the necessary compliance invoices"""
    def __init__(self, detail: str | None = "You are not allowed to switch to production at the moment because you haven't finished uploading the compliance invoices. You have to upload one invoice of each type of your invoicing type with its credit and debit notes (at least one invoice, credit note and debit note for each type of your invoicing type).", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)
    