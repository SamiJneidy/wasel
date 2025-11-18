from fastapi import APIRouter, Query, Request, status
from src.core.schemas import SingleObjectResponse
from .services import UserService
from .schemas import (
    UserInviteRequest,
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


@router.post(
    "/invite",
    response_model=SingleObjectResponse[UserOut],
    # responses=RESPONSES["sign_up_complete"],
    # summary=SUMMARIES["sign_up_complete"],
    # description=DOCSTRINGS["sign_up_complete"],
)
async def invite_user(
    request: Request,
    body: UserInviteRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user_email: Annotated[str, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    data = await user_service.invite_user(current_user_email, request.base_url, body)
    return SingleObjectResponse(data=data)



@router.post(
    "/invite/resend",
    response_model=SingleObjectResponse[UserOut],
    # responses=RESPONSES["sign_up_complete"],
    # summary=SUMMARIES["sign_up_complete"],
    # description=DOCSTRINGS["sign_up_complete"],
)
async def resend_invitation(
    request: Request,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user_email: Annotated[UserOut, Depends(get_current_user)],
    email: str = Query(description="Email of the user to send invitation to."),
) -> SingleObjectResponse[UserOut]:
    data = await user_service.send_invitation(email, request.base_url)
    return SingleObjectResponse(data=data)


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