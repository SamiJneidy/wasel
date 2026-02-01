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

class RoleNotFoundException(BaseAppException):
    """Raised when the role is not found."""
    def __init__(self, detail: str | None = "Role not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)

class RoleCannotBeDeletedException(BaseAppException):
    """Raised when the role cannot be deleted due to existing dependencies."""
    def __init__(self, detail: str | None = "Role cannot be deleted", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class RoleImmutableException(BaseAppException):
    """Raised when trying to modify an immutable role."""
    def __init__(self, detail: str | None = "Role is immutable", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class InvalidBranchesException(BaseAppException):
    """Raised when the branches set for a user are not valid."""
    def __init__(self, detail: str | None = "Invalid list of branches", status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        super().__init__(detail, status_code)
