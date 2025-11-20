from fastapi import APIRouter, Query, Request, status
from src.core.schemas import SingleObjectResponse, ObjectListResponse
from src.core.database import AsyncSession, get_db
from .services import UserService
from .schemas import UserInDB, UserInvite, UserOut
from .dependencies import Annotated, Depends, get_user_service
from src.core.dependencies import get_current_user
from src.docs.users import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    path="/",
    response_model=ObjectListResponse[UserOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_users(  
    current_user_email: Annotated[str, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ObjectListResponse[UserOut]:
    current_user = await user_service.get_by_email(current_user_email)
    data = await user_service.get_users_by_org(current_user.organization.id)
    return ObjectListResponse(data=data)


@router.get(
    path="/",
    response_model=ObjectListResponse[UserOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_users(  
    current_user_email: Annotated[str, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ObjectListResponse[UserOut]:
    current_user = await user_service.get_by_email(current_user_email)
    data = await user_service.get_users_by_org(current_user.organization.id)
    return ObjectListResponse(data=data)


# -----------------------
# GET USER BY ID
# -----------------------
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
    return SingleObjectResponse(data=data)


# -----------------------
# GET USER BY EMAIL
# -----------------------
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
    return SingleObjectResponse(data=data)


# -----------------------
# INVITE USER
# -----------------------
@router.post(
    "/invitations",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES.get("invite_user"),
    summary=SUMMARIES.get("invite_user"),
    description=DOCSTRINGS.get("invite_user"),
)
async def invite_user(
    request: Request,
    body: UserInvite,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    # Transaction ensures rollback if email sending or user creation fails
    async with db.begin():
        data = await user_service.invite_user(current_user, request.base_url, body)
    return SingleObjectResponse(data=data)


# -----------------------
# RESEND INVITATION
# -----------------------
@router.post(
    "/invitations/resend",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES.get("resend_invitation"),
    summary=SUMMARIES.get("resend_invitation"),
    description=DOCSTRINGS.get("resend_invitation"),
)
async def resend_invitation(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    email: str = Query(..., description="Email of the user to send invitation to."),
) -> SingleObjectResponse[UserOut]:
    async with db.begin():
        data = await user_service.send_invitation(current_user, email, request.base_url)
    return SingleObjectResponse(data=data)


# -----------------------
# DELETE USER
# -----------------------
@router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["delete_user"],
    summary=SUMMARIES["delete_user"],
    description=DOCSTRINGS["delete_user"],
)
async def delete_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    email: str = Query(..., description="Email of the user to delete."),
) -> None:
    await user_service.delete_user(email)
