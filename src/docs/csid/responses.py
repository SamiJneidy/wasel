from fastapi import status
from src.core.schemas import ErrorResponse

RESPONSES = {
    "generate_compliance_csid": {
        status.HTTP_200_OK: {"description": "Compliance CSID generated successfully."},
        status.HTTP_403_FORBIDDEN: {"description": "User sign-up is not complete.", "model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"description": "ZATCA rejected the request (e.g., invalid OTP or invalid request).", "model": ErrorResponse},
        status.HTTP_408_REQUEST_TIMEOUT: {"description": "Failed to reach ZATCA or request timed out.", "model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
    },
    "generate_production_csid": {
        status.HTTP_200_OK: {"description": "Production CSID generated successfully and user switched to production."},
        status.HTTP_403_FORBIDDEN: {"description": "User sign-up is not complete or switching to production is not allowed yet.", "model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"description": "ZATCA rejected the request.", "model": ErrorResponse},
        status.HTTP_408_REQUEST_TIMEOUT: {"description": "Failed to reach ZATCA or request timed out.", "model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
    },
} 