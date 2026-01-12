from fastapi import status
from src.core.exceptions.exceptions import BaseAppException

class PointOfSaleNotFoundException(BaseAppException):
    def __init__(self, detail: str | None = "Point of sale not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)
        