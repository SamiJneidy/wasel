from fastapi import APIRouter, status
from src.core.schemas import SingleObjectResponse
from .services import UserService
from .schemas import (
    UserOut,
)
from .dependencies import (
    Annotated,
    Depends, 
    get_user_service,
)
from src.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/users", 
    tags=["Users"],
)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[UserOut],
    responses={
        status.HTTP_200_OK: {
            "description": "User was returned successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UesrNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def get(
    id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SingleObjectResponse[UserOut]:
    """Get user by id.""" 
    data = await user_service.get(id)
    return SingleObjectResponse[UserOut](data=data)


@router.get(
    path="/email/{email}",
    response_model=SingleObjectResponse[UserOut],
    responses={
        status.HTTP_200_OK: {
            "description": "User was returned successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UesrNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def get(
    email: str,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SingleObjectResponse[UserOut]:
    """Get user by id.""" 
    data = await user_service.get_by_email(email)
    return SingleObjectResponse[UserOut](data=data)


# @router.patch(
#     path="/{id}",
#     response_model=SingleObjectResponse[UserOut],
#     responses={
#         status.HTTP_200_OK: {
#             "description": "Updated user successfully."
#         },
#         status.HTTP_404_NOT_FOUND: {
#             "description": "User was not found.",
#             "content": {
#                 "application/json": {
#                     "examples": {
#                         "UserNotFound": {
#                             "value": {
#                                 "detail": "User not found"
#                             }
#                         },
#                     }
#                 }
#             }
#         },
#     }
# )
# async def update(
#     id: int, 
#     data: UserUpdate,
#     user_service: Annotated[UserService, Depends(get_user_service)],
#     current_user: Annotated[UserOut, Depends(get_current_user)],
# ) -> SingleObjectResponse[UserOut]:
#     """Update user by id"""
#     data = await user_service.update(id, data)
#     return SingleObjectResponse[UserOut](data=data)


@router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
        responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "User has beed deleted successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },
                    }
                }
            }
        },
    }
)
async def delete_user(
    email: str,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    """Deletes a user by email. This endpoint for development only."""
    await user_service.delete_user(email)