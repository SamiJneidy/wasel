from typing import Annotated

from fastapi import APIRouter, status, Depends

from src.tax_authorities.schemas import BranchTaxAuthorityDataComplete, BranchTaxAuthorityDataCreate, BranchTaxAuthorityDataUpdate

from .services import BranchService
from src.core.schemas.common import ObjectListResponse, SingleObjectResponse
from src.core.schemas.context import RequestContext
from .schemas import (
    BranchCreate,
    BranchUpdate,
    BranchOutWithTaxAuthority,
)
from .dependencies.services import get_branch_service
from src.core.dependencies.auth import get_request_context
from src.core.dependencies.authorization import require_permission
from src.docs.branches import RESPONSES, DOCSTRINGS, SUMMARIES
router = APIRouter(
    prefix="/branches",
    tags=["Branches"],
)


# ---------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------
@router.get(
    path="",
    response_model=ObjectListResponse[BranchOutWithTaxAuthority],
    # responses=RESPONSES["get_branches_for_user"],
    # summary=SUMMARIES["get_branches_for_user"],
    # description=DOCSTRINGS["get_branches_for_user"],
)
async def get_branches(
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    permission = Depends(require_permission("branches", "read")),
) -> ObjectListResponse[BranchOutWithTaxAuthority]:
    data = await branch_service.get_branches(request_context)
    return ObjectListResponse(data=data)


# ---------------------------------------------------------------------

@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[BranchOutWithTaxAuthority],
    # responses=RESPONSES["get_branch"],
    # summary=SUMMARIES["get_branch"],
    # description=DOCSTRINGS["get_branch"],
)
async def get_branch(
    id: int,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    permission = Depends(require_permission("branches", "read")),
) -> SingleObjectResponse[BranchOutWithTaxAuthority]:
    data = await branch_service.get_branch(request_context, id)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------
# POST routes
# ---------------------------------------------------------------------
@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[BranchOutWithTaxAuthority],
    # responses=RESPONSES["create_branch"],
    # summary=SUMMARIES["create_branch"],
    # description=DOCSTRINGS["create_branch"],
)
async def create_branch(
    body: BranchCreate,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    permission = Depends(require_permission("branches", "create")),
) -> SingleObjectResponse[BranchOutWithTaxAuthority]:
    data = await branch_service.create_branch(request_context, body)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------

@router.post(
    path="/tax-authority-data",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[BranchOutWithTaxAuthority],
    # responses=RESPONSES["create_branch"],
    # summary=SUMMARIES["create_branch"],
    # description=DOCSTRINGS["create_branch"],
)
async def create_branch_tax_authority_data(
    body: BranchTaxAuthorityDataCreate,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[BranchOutWithTaxAuthority]:
    data = await branch_service.create_branch_tax_authority_data(request_context, body)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------

@router.post(
    path="/tax-authority-data/complete",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[BranchOutWithTaxAuthority],
    # responses=RESPONSES["create_branch"],
    # summary=SUMMARIES["create_branch"],
    # description=DOCSTRINGS["create_branch"],
)
async def complete_branch_tax_authority_data(
    body: BranchTaxAuthorityDataComplete,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[BranchOutWithTaxAuthority]:
    data = await branch_service.complete_branch_tax_authority_data(request_context, body)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------
# PUT routes
# ---------------------------------------------------------------------

@router.put(
    path="/tax-authority-data",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[BranchOutWithTaxAuthority],
    # responses=RESPONSES["create_branch"],
    # summary=SUMMARIES["create_branch"],
    # description=DOCSTRINGS["create_branch"],
)
async def update_branch_tax_authority_data(
    body: BranchTaxAuthorityDataUpdate,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[BranchOutWithTaxAuthority]:
    data = await branch_service.update_branch_tax_authority_data(request_context, body)
    return SingleObjectResponse(data=data)

@router.put(
    path="/{id}",
    response_model=SingleObjectResponse[BranchOutWithTaxAuthority],
    # responses=RESPONSES["update_branch"],
    # summary=SUMMARIES["update_branch"],
    # description=DOCSTRINGS["update_branch"],
)
async def update_branch(
    id: int,
    body: BranchUpdate,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    permission = Depends(require_permission("branches", "update")),
) -> SingleObjectResponse[BranchOutWithTaxAuthority]:
    data = await branch_service.update_branch(request_context, id, body)
    return SingleObjectResponse(data=data)


# ---------------------------------------------------------------------
# DELETE routes
# ---------------------------------------------------------------------
@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # responses=RESPONSES["delete_branch"],
    # summary=SUMMARIES["delete_branch"],
    # description=DOCSTRINGS["delete_branch"],
)
async def delete_branch(
    id: int,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    permission = Depends(require_permission("branches", "delete")),
) -> None:
    await branch_service.delete_branch(request_context, id)
    return None
