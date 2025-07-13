from fastapi import status

class BaseAppException(Exception):
    def __init__(self, detail: str = "An error has occurred.", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.detail = detail
        self.status_code = status_code

class ResourceAlreadyInUseException(BaseAppException):
    def __init__(self, resource_name: str = "Resource", detail: str = None):
        detail = detail or f"{resource_name} already in use."
        super().__init__(detail, status.HTTP_409_CONFLICT)

class ResourceNotFoundException(BaseAppException):
    def __init__(self, resource_name: str = "Resource", detail: str = None):
        detail = detail or f"{resource_name} not found."
        super().__init__(detail, status.HTTP_404_NOT_FOUND)
