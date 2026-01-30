from math import ceil

from fastapi import APIRouter, status

from src.core.dependencies.auth import get_request_context
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
# from src.docs.projects import DOCSTRINGS, RESPONSES, SUMMARIES
from src.core.schemas.context import RequestContext

from .dependencies import Annotated, Depends, get_project_service
from .schemas import ProjectCreate, ProjectFilters, ProjectOut, ProjectUpdate
from .services import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


# =========================================================
# GET routes
# =========================================================

@router.get(
    path="",
    response_model=PaginatedResponse[ProjectOut],
    # responses=RESPONSES["get_projects_for_user"],
    # summary=SUMMARIES["get_projects_for_user"],
    # description=DOCSTRINGS["get_projects_for_user"],
)
async def get_projects(
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    pagination_params: PagintationParams = Depends(),
    filters: ProjectFilters = Depends(),
) -> PaginatedResponse[ProjectOut]:
    total_rows, data = await project_service.get_projects(
        request_context,
        pagination_params,
        filters,
    )
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=(
            ceil(total_rows / pagination_params.limit)
            if pagination_params.limit is not None
            else 1
        ),
        page=pagination_params.page,
        limit=pagination_params.limit,
    )


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[ProjectOut],
    # responses=RESPONSES["get_project"],
    # summary=SUMMARIES["get_project"],
    # description=DOCSTRINGS["get_project"],
)
async def get_project(
    id: int,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[ProjectOut]:
    data = await project_service.get_project(request_context, id)
    return SingleObjectResponse(data=data)


# =========================================================
# POST routes
# =========================================================

@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[ProjectOut],
    # responses=RESPONSES["create_project"],
    # summary=SUMMARIES["create_project"],
    # description=DOCSTRINGS["create_project"],
)
async def create_project(
    body: ProjectCreate,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[ProjectOut]:
    data = await project_service.create_project(request_context, body)
    return SingleObjectResponse(data=data)


# =========================================================
# PATCH routes
# =========================================================

@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[ProjectOut],
    # responses=RESPONSES["update_project"],
    # summary=SUMMARIES["update_project"],
    # description=DOCSTRINGS["update_project"],
)
async def update_project(
    id: int,
    body: ProjectUpdate,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[ProjectOut]:
    data = await project_service.update_project(request_context, id, body)
    return SingleObjectResponse(data=data)


# =========================================================
# DELETE routes
# =========================================================

@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # responses=RESPONSES["delete_project"],
    # summary=SUMMARIES["delete_project"],
    # description=DOCSTRINGS["delete_project"],
)
async def delete_project(
    id: int,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> None:
    return await project_service.delete_project(request_context, id)
