from fastapi import status
from src.core.schemas import ErrorResponse

RESPONSES = {
    "create_invoice": {
        status.HTTP_201_CREATED: {"description": "Invoice created and submitted successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid data, signing error, or integrity error.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Customer or item not found.", "model": ErrorResponse},
        status.HTTP_408_REQUEST_TIMEOUT: {"description": "Failed to reach ZATCA or request timed out.", "model": ErrorResponse},
    },
    "get_invoice": {
        status.HTTP_200_OK: {"description": "Invoice retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Invoice not found.", "model": ErrorResponse},
    },
} 