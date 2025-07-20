from fastapi import status
from src.core.exceptions import BaseAppException, ResourceNotFoundException
from src.users.exceptions import UserNotCompleteException

class RequestNotSentException(BaseAppException):
    """Raised when the request could not be sent."""
    def __init__(self, detail: str = "Could not send the request", status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE):
        super().__init__(detail, status_code)
