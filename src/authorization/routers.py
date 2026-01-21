from math import ceil
from fastapi import APIRouter, Query, Request, Depends
from typing import Annotated
from src.core.schemas import SingleObjectResponse, ObjectListResponse, PagintationParams, PaginatedResponse
from .schemas import UserPermissionCreate, UserPermissionUpdate, UserPermissionOut, PermissionOut, RoleCreate, RoleUpdate, RoleWithPermissionsOut
from src.users.schemas import UserInDB
from .dependencies import AuthorizationService, get_authorization_service
from src.users.dependencies import UserService, get_user_service
from src.core.dependencies.shared import get_current_user
from src.docs.users import RESPONSES, DOCSTRINGS, SUMMARIES
from fastapi import status

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
    path="/roles",
    response_model=ObjectListResponse[RoleWithPermissionsOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_roles(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> ObjectListResponse[RoleWithPermissionsOut]:
    role = await authorization_service.get_roles(current_user)
    return ObjectListResponse(data=role)

@router.get(
    path="/roles/{role_id}",
    response_model=SingleObjectResponse[RoleWithPermissionsOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_role(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    role_id: int,
) -> SingleObjectResponse[RoleWithPermissionsOut]:
    role = await authorization_service.get_role(current_user, role_id)
    return SingleObjectResponse(data=role)

@router.get(
    path="/permissions/user/{user_id}",
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
# POST routes
# ---------------------------------------------------------------------
@router.post(
    path="/roles",
    response_model=SingleObjectResponse[RoleWithPermissionsOut],
)
async def create_role(
    data: RoleCreate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> SingleObjectResponse[RoleWithPermissionsOut]:
    role = await authorization_service.create_role(current_user, data)
    return SingleObjectResponse(data=role)


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

@router.put(
    path="/roles/{role_id}",
    response_model=SingleObjectResponse[RoleWithPermissionsOut],
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> SingleObjectResponse[RoleWithPermissionsOut]:
    role = await authorization_service.update_role(current_user, role_id, data)
    return SingleObjectResponse(data=role)


# ---------------------------------------------------------------------
# DELETE routes
# ---------------------------------------------------------------------
@router.delete(
    path="roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(
    role_id: int,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> None:
    await authorization_service.delete_role(current_user, role_id)