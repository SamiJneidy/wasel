from fastapi import status
from src.core.exceptions import BaseAppException, ResourceNotFoundException

class UserNotFoundException(BaseAppException):
    """Raised when the user is not found."""
    def __init__(self, detail: str = "User not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)

class UserNotActiveException(BaseAppException):
    """Raised when the user is not active."""
    def __init__(self, detail: str = "Your accounts is not active. You can not perform the action.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class UserNotCompleteException(BaseAppException):
    """Raised when the user is not complete."""
    def __init__(self, detail: str = "The user has not completed the sign up.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class UserBlockedException(BaseAppException):
    """Raised when a blocked user tries to perform an action."""
    def __init__(self, detail: str = "Your accounts is blocked. Please contact the support to discuss the issue.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)        
    
class UserDisabledException(BaseAppException):
    """Raised when a disabled user tries to perform an action."""
    def __init__(self, detail: str = "Your account is disabled. This usually happens due to security reasons or multiple invalid login attempts. Please reset your password and try again.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)        
    
class UserNotPendingException(BaseAppException):
    """Raised when trying to send an OTP code for email verification while the user status is not PENDING."""
    def __init__(self, detail: str = "User status is not pending to verify the email", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class UserNotVerifiedException(BaseAppException):
    """Raised when the user's email is not verified."""
    def __init__(self, detail: str = "Your account is not verified. Verify your account and try again.", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)
