from fastapi import status
from src.core.exceptions.exceptions import BaseAppException

class BranchNotFoundException(BaseAppException):
    def __init__(self, detail: str | None = "Branch not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)


class BranchTaxAuthorityDataFoundException(BaseAppException):
    def __init__(self, detail: str | None = "The current branch already has tax authority data", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class BranchTaxAuthorityDataUpdateForbiddenException(BaseAppException):
    def __init__(self, detail: str | None = "Cannot update tax authority data for this branch", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)
        