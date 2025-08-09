from fastapi import status

class BaseAppException(Exception):
    def __init__(self, detail: str | None = "An error has occurred.", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.detail = detail
        self.status_code = status_code


class RequestCouldNotBeSent(BaseAppException):
    def __init__(self, detail: str | None = "Request could not be sent.", status_code: int = status.HTTP_408_REQUEST_TIMEOUT):
        super().__init__(detail, status_code)


class IntegrityErrorException(BaseAppException):
    def __init__(self, detail: str | None = (
        "A database integrity error occurred. "
        "This may be due to a unique, foreign key, not-null, or check constraint violation."
    )):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class UniqueConstraintViolationException(BaseAppException):
    def __init__(self, detail: str | None = (
        "Unique constraint violation: A record with the same unique value already exists."
    )):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ForeignKeyViolationException(BaseAppException):
    def __init__(self, detail: str | None = (
        "Foreign key constraint violation: Referenced record does not exist."
    )):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class NotNullConstraintViolationException(BaseAppException):
    def __init__(self, detail: str | None = (
        "Not-null constraint violation: A required field was left null."
    )):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class CheckConstraintViolationException(BaseAppException):
    def __init__(self, detail: str | None = (
        "Check constraint violation: A column value failed a custom validation rule."
    )):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)
