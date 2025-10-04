from fastapi import status
from src.core.schemas import ErrorResponse

RESPONSES = {
    "create_supplier": {
        status.HTTP_201_CREATED: {"description": "Supplier created successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
    },
    "update_supplier": {
        status.HTTP_200_OK: {"description": "Supplier updated successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Supplier not found.", "model": ErrorResponse},
    },
    "delete_supplier": {
        status.HTTP_204_NO_CONTENT: {"description": "Supplier deleted successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Supplier not found.", "model": ErrorResponse},
    },
    "get_suppliers_for_user": {
        status.HTTP_200_OK: {"description": "Suppliers retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
    },
    "get_supplier": {
        status.HTTP_200_OK: {"description": "Supplier retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Supplier not found.", "model": ErrorResponse},
    },
} 