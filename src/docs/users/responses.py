from fastapi import status
from src.core.schemas import ErrorResponse

RESPONSES = {
    "get_user_by_id": {
        status.HTTP_200_OK: {"description": "User retrieved successfully."},
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found. Returned when the user id does not exist or is not accessible.",
            "model": ErrorResponse,
        },
    },
    "get_user_by_email": {
        status.HTTP_200_OK: {"description": "User retrieved successfully."},
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found. Returned when the email does not correspond to any user.",
            "model": ErrorResponse,
        },
    },
    "delete_user": {
        status.HTTP_204_NO_CONTENT: {"description": "User deleted successfully."},
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found. Returned when the email does not correspond to any user.",
            "model": ErrorResponse,
        },
    },
} 