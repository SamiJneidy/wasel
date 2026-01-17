from math import ceil
from fastapi import APIRouter, Query, Request, Depends
from typing import Annotated
from src.core.schemas import SingleObjectResponse, ObjectListResponse, PagintationParams, PaginatedResponse
from .schemas import UserPermissionCreate, UserPermissionUpdate, UserPermissionOut, PermissionOut
from src.users.schemas import UserInDB
from .dependencies import AuthorizationService, get_authorization_service
from src.users.dependencies import UserService, get_user_service
from src.core.dependencies.shared import get_current_user
from src.docs.users import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/authorization",
    tags=["Authorization"],
)


# ---------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------

@router.get(
    path="/permissions",
    response_model=ObjectListResponse[PermissionOut],
)
async def get_permissions(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> ObjectListResponse[PermissionOut]:
    data = await authorization_service.get_permissions()
    return ObjectListResponse(data=data)


@router.get(
    path="/permissions/{user_id}",
    response_model=SingleObjectResponse[UserPermissionOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_user_permissions(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_id: int,
) -> SingleObjectResponse[UserPermissionOut]:
    user = await user_service.get(user_id)
    permissions = await authorization_service.get_user_permissions(current_user, user_id)
    data = UserPermissionOut(permissions=permissions)
    return SingleObjectResponse(data=data)

# ---------------------------------------------------------------------
# PUT routes
# ---------------------------------------------------------------------

@router.put(
    path="/permissions/{user_id}",
    response_model=SingleObjectResponse[UserPermissionOut],
)
async def update_user_permissions(
    user_id: int,
    data: UserPermissionUpdate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SingleObjectResponse[UserPermissionOut]:
    user = await user_service.get(user_id)
    permissions = await authorization_service.update_user_permissions(current_user, user_id, data)
    data = UserPermissionOut(permissions=permissions)
    return SingleObjectResponse(data=data)
