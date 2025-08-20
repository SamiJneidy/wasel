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
from src.docs.users import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/users", 
    tags=["Users"],
)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES["get_user_by_id"],
    summary=SUMMARIES["get_user_by_id"],
    description=DOCSTRINGS["get_user_by_id"],
)
async def get_user_by_id(
    id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SingleObjectResponse[UserOut]:
    data = await user_service.get(id)
    return SingleObjectResponse[UserOut](data=data)


@router.get(
    path="/email/{email}",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES["get_user_by_email"],
    summary=SUMMARIES["get_user_by_email"],
    description=DOCSTRINGS["get_user_by_email"],
)
async def get_user_by_email(
    email: str,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SingleObjectResponse[UserOut]:
    data = await user_service.get_by_email(email)
    return SingleObjectResponse[UserOut](data=data)


@router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["delete_user"],
    summary=SUMMARIES["delete_user"],
    description=DOCSTRINGS["delete_user"],
)
async def delete_user(
    email: str,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    await user_service.delete_user(email)