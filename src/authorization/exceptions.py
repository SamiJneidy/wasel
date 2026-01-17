from fastapi import status
from src.core.exceptions.exceptions import BaseAppException

class InvalidPermissionException(BaseAppException):
    """Raised when the permission is not present on the permissions."""
    def __init__(self, detail: str | None = "Invalid permission", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class PermissionDeniedException(BaseAppException):
    """Raised when the user does not have the required permission."""
    def __init__(self, detail: str | None = "Permission denied", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)