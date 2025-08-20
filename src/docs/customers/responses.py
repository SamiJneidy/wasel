from fastapi import status
from src.core.schemas import ErrorResponse

RESPONSES = {
    "create_customer": {
        status.HTTP_201_CREATED: {"description": "Customer created successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
    },
    "update_customer": {
        status.HTTP_200_OK: {"description": "Customer updated successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found.", "model": ErrorResponse},
    },
    "delete_customer": {
        status.HTTP_204_NO_CONTENT: {"description": "Customer deleted successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found.", "model": ErrorResponse},
    },
    "get_customers_for_user": {
        status.HTTP_200_OK: {"description": "Customers retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
    },
    "get_customer": {
        status.HTTP_200_OK: {"description": "Customer retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found.", "model": ErrorResponse},
    },
} 