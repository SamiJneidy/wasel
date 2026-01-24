from math import ceil
from fastapi import APIRouter, Query, Request
from typing import Annotated
from src.core.schemas import SingleObjectResponse, ObjectListResponse, PagintationParams, PaginatedResponse
from .schemas import UserInDB, UserInvite, UserOut, UserFilters
from .dependencies import UserService, Depends, get_user_service
from src.core.dependencies.shared import get_current_user
from src.docs.users import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ---------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------
@router.get(
    path="",
    response_model=PaginatedResponse[UserOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_users(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    pagination_params: Annotated[PagintationParams, Depends()],
    filters: Annotated[UserFilters, Depends()],
) -> PaginatedResponse[UserOut]:
    total_rows, data = await user_service.get_users_by_org_id(current_user.organization_id, pagination_params, filters)
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=ceil(total_rows/pagination_params.limit) if pagination_params.limit is not None else 1,
        page=pagination_params.page,
        limit=pagination_params.limit
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
    return SingleObjectResponse(data=data)


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


# ---------------------------------------------------------------------
# POST routes
# ---------------------------------------------------------------------
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
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    data = await user_service.invite_user(current_user, str(request.base_url), body)
    return SingleObjectResponse(data=data)


@router.post(
    "/invitations/resend/{user_id}",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES.get("resend_invitation"),
    summary=SUMMARIES.get("resend_invitation"),
    description=DOCSTRINGS.get("resend_invitation"),
)
async def resend_invitation(
    request: Request,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    user_id: int,
) -> SingleObjectResponse[UserOut]:
    user = await user_service.get(user_id)
    data = await user_service.send_invitation(current_user, user.email, request.base_url)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------
# DELETE routes
# ---------------------------------------------------------------------
@router.delete(
    path="/",
    status_code=204,
    responses=RESPONSES["delete_user"],
    summary=SUMMARIES["delete_user"],
    description=DOCSTRINGS["delete_user"],
)
async def delete_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    email: str = Query(..., description="Email of the user to delete."),
) -> None:
    await user_service.delete_user(email)
