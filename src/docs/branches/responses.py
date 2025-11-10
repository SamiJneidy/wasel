from fastapi import status
from src.core.schemas import ErrorResponse

RESPONSES = {
    "create_item": {
        status.HTTP_201_CREATED: {"description": "Item created successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error in request body.", "model": ErrorResponse},
    },
    "update_item": {
        status.HTTP_200_OK: {"description": "Item updated successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Item not found.", "model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error in request body.", "model": ErrorResponse},
    },
    "delete_item": {
        status.HTTP_204_NO_CONTENT: {"description": "Item deleted successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Item not found.", "model": ErrorResponse},
    },
    "get_items_for_user": {
        status.HTTP_200_OK: {"description": "Items retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
    },
    "get_item": {
        status.HTTP_200_OK: {"description": "Item retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing access token.", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Item not found.", "model": ErrorResponse},
    },
} 