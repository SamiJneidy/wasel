from fastapi import status
from src.core.exceptions.exceptions import BaseAppException
from src.users.exceptions import (
    UserNotFoundException, 
    UserNotActiveException, 
    UserBlockedException, 
    UserDisabledException, 
    UserNotVerifiedException,
)


# Auth
class PasswordResetNotAllowedException(BaseAppException):
    """Raised when trying to reset the password without verifying the OTP code or the email is blocked."""
    def __init__(self, detail: str | None = "Password reset not allowed. This may haapen because of invlid or expired OTP code or for other security issues. Please request a new OTP code and try again.", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class PasswordsDontMatchException(BaseAppException):
    """Raised when reseting the password and the provided passwords don't match."""
    def __init__(self, detail: str | None = "Passwords don't match", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class InvalidCredentialsException(BaseAppException):
    """Raised when trying to login but the credentials are invalid."""
    def __init__(self, detail: str | None = "Invalid credentials", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class EmailAlreadyInUseException(BaseAppException):
    """Raised when the email is already in use."""
    def __init__(self, detail: str | None = "Email already in use", status_code: int = status.HTTP_409_CONFLICT):
        super().__init__(detail, status_code)

class InvalidTokenException(BaseAppException):
    """Raised the token is invalid or expired."""
    def __init__(self, detail: str | None = "Invalid token", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)



# OTP
class InvalidOTPException(BaseAppException):
    """Raised when the OTP code is invalid."""
    def __init__(self, detail: str | None = "The OTP code is invalid or has expired or has been used before", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class ExpiredOTPException(BaseAppException):
    """Raised when the OTP code is expired."""
    def __init__(self, detail: str | None = "OTP code has expired", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class OTPAlreadyUsedException(BaseAppException):
    """Raised when the OTP has already been used and cannot be reused."""
    def __init__(self, detail: str | None = "The OTP code has been used before", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class MultipleOTPsDetectedException(BaseAppException):
    """Raised when multiple OTP codes are found for a single user."""
    def __init__(self, detail: str | None = "OTP verification error", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class SuspiciousOTPActivityException(BaseAppException):
    """Raised when a security issue is detected with the OTP process."""
    def __init__(self, detail: str | None = "Unusual activiy has been detected. Operation aborted for security issues.", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class OTPNotFoundException(BaseAppException):
    """Raised when the OTP is not found."""
    def __init__(self, detail: str | None = "OTP not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)

class OTPCouldNotBeSentException(BaseAppException):
    """Raised when the OTP could not be sent to the email."""
    def __init__(self, detail: str | None = "OTP could not be sent to the email", status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE):
        super().__init__(detail, status_code)

