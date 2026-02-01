from math import ceil
from fastapi import APIRouter, Query, Request, Depends
from typing import Annotated
from src.core.schemas import SingleObjectResponse, ObjectListResponse, PagintationParams, PaginatedResponse
from .schemas import UserPermissionCreate, UserPermissionUpdate, UserPermissionOut, PermissionInDB, RoleCreate, RoleUpdate, RoleWithPermissionsOut
from src.core.schemas.context import RequestContext
from .dependencies import AuthorizationService, get_authorization_service
from src.users.dependencies.services import UserService, get_user_service
from src.core.dependencies.auth import get_request_context
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
    response_model=ObjectListResponse[PermissionInDB],
)
async def get_permissions(
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> ObjectListResponse[PermissionInDB]:
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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> ObjectListResponse[RoleWithPermissionsOut]:
    role = await authorization_service.get_roles(request_context)
    return ObjectListResponse(data=role)

@router.get(
    path="/roles/{role_id}",
    response_model=SingleObjectResponse[RoleWithPermissionsOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_role(
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    role_id: int,
) -> SingleObjectResponse[RoleWithPermissionsOut]:
    role = await authorization_service.get_role(request_context, role_id)
    return SingleObjectResponse(data=role)

@router.get(
    path="/user/{user_id}/permissions",
    response_model=SingleObjectResponse[UserPermissionOut],
    # responses=RESPONSES["get_user_by_email"],
    # summary=SUMMARIES["get_user_by_email"],
    # description=DOCSTRINGS["get_user_by_email"],
)
async def get_user_permissions(
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_id: int,
) -> SingleObjectResponse[UserPermissionOut]:
    user = await user_service.get_user(user_id)
    data = await authorization_service.get_user_permissions(request_context, user_id)
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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> SingleObjectResponse[RoleWithPermissionsOut]:
    role = await authorization_service.create_role(request_context, data)
    return SingleObjectResponse(data=role)


# ---------------------------------------------------------------------
# PUT routes
# ---------------------------------------------------------------------

@router.put(
    path="/users/{user_id}/permissions",
    response_model=SingleObjectResponse[UserPermissionOut],
)
async def update_user_permissions(
    user_id: int,
    body: UserPermissionUpdate,
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SingleObjectResponse[UserPermissionOut]:
    user = await user_service.get_user(user_id)
    data = await authorization_service.update_user_permissions(request_context, user_id, body)
    return SingleObjectResponse(data=data)

@router.put(
    path="/roles/{role_id}",
    response_model=SingleObjectResponse[RoleWithPermissionsOut],
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> SingleObjectResponse[RoleWithPermissionsOut]:
    role = await authorization_service.update_role(request_context, role_id, data)
    return SingleObjectResponse(data=role)


# ---------------------------------------------------------------------
# DELETE routes
# ---------------------------------------------------------------------
@router.delete(
    path="/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(
    role_id: int,
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> None:
    await authorization_service.delete_role(request_context, role_id)