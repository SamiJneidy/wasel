from typing import Annotated

from fastapi import APIRouter, status, Depends
from src.core.schemas.context import RequestContext
from .services import OrganizationService
from .schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationOut,
    ObjectListResponse,
    SingleObjectResponse,
)
from .dependencies import get_organization_service
from src.core.dependencies.auth import get_request_context
from src.docs.organizations import RESPONSES, DOCSTRINGS, SUMMARIES


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


# ---------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------
@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[OrganizationOut],
    # responses=RESPONSES["get_organization"],
    # summary=SUMMARIES["get_organization"],
    # description=DOCSTRINGS["get_organization"],
)
async def get_organization(
    id: int,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[OrganizationOut]:
    data = await organization_service.get_organization(id)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------
# POST routes
# ---------------------------------------------------------------------
@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[OrganizationOut],
    # responses=RESPONSES["create_organization"],
    # summary=SUMMARIES["create_organization"],
    # description=DOCSTRINGS["create_organization"],
)
async def create_organization(
    body: OrganizationCreate,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[OrganizationOut]:
    data = await organization_service.create_organization(request_context, body)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------
# PATCH routes
# ---------------------------------------------------------------------
@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[OrganizationOut],
    # responses=RESPONSES["update_organization"],
    # summary=SUMMARIES["update_organization"],
    # description=DOCSTRINGS["update_organization"],
)
async def update_organization(
    id: int,
    body: OrganizationUpdate,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[OrganizationOut]:
    data = await organization_service.update_organization(id, body)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------
# DELETE routes
# ---------------------------------------------------------------------
@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # responses=RESPONSES["delete_organization"],
    # summary=SUMMARIES["delete_organization"],
    # description=DOCSTRINGS["delete_organization"],
)
async def delete_organization(
    id: int,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> None:
    await organization_service.delete_organization(request_context, id)
    return None
