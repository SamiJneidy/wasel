from fastapi import status
from src.core.exceptions.exceptions import BaseAppException

class OrganizationNotFoundException(BaseAppException):
    def __init__(self, detail: str | None = "Item not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)
        