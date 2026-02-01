from fastapi import status
from src.core.exceptions.exceptions import BaseAppException

class OrganizationNotFoundException(BaseAppException):
    def __init__(self, detail: str | None = "Organization not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)
        

class TaxAuthorityUpdateNotAllowedException(BaseAppException):
    def __init__(self, detail: str | None = "Tax authority update not allowed. It's forbidden to downgrade tax authrity.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)
        