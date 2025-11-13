from fastapi import status
from ..exceptions import BaseAppException

class EmailCouldNotBeSentException(BaseAppException):
    """Raised when an email could not be sent."""
    def __init__(self, detail: str | None = "Email could not be sent.", status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE):
        super().__init__(detail, status_code)