from src.core.utils.math_helper import calc_total_pages
from fastapi import APIRouter, status

from src.core.dependencies.auth import get_request_context
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
from src.docs.items import DOCSTRINGS, RESPONSES, SUMMARIES
from src.core.schemas.context import RequestContext

from .dependencies import Annotated, Depends, get_item_service
from .schemas import ItemCreate, ItemFilters, ItemOut, ItemUpdate
from .services import ItemService

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)


# =========================================================
# GET routes
# =========================================================

@router.get(
    path="",
    response_model=PaginatedResponse[ItemOut],
    responses=RESPONSES["get_items_for_user"],
    summary=SUMMARIES["get_items_for_user"],
    description=DOCSTRINGS["get_items_for_user"],
)
async def get_items(
    item_service: Annotated[ItemService, Depends(get_item_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    pagination_params: PagintationParams = Depends(),
    filters: ItemFilters = Depends(),
) -> PaginatedResponse[ItemOut]:
    total_rows, data = await item_service.get_items(
        request_context,
        pagination_params,
        filters,
    )
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=calc_total_pages(total_rows, pagination_params.limit),
        page=pagination_params.page,
        limit=pagination_params.limit,
    )


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[ItemOut],
    responses=RESPONSES["get_item"],
    summary=SUMMARIES["get_item"],
    description=DOCSTRINGS["get_item"],
)
async def get_item(
    id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[ItemOut]:
    data = await item_service.get_item(request_context, id)
    return SingleObjectResponse(data=data)


# =========================================================
# POST routes
# =========================================================

@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[ItemOut],
    responses=RESPONSES["create_item"],
    summary=SUMMARIES["create_item"],
    description=DOCSTRINGS["create_item"],
)
async def create_item(
    body: ItemCreate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[ItemOut]:
    data = await item_service.create_item(request_context, body)
    return SingleObjectResponse(data=data)


# =========================================================
# PATCH routes
# =========================================================

@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[ItemOut],
    responses=RESPONSES["update_item"],
    summary=SUMMARIES["update_item"],
    description=DOCSTRINGS["update_item"],
)
async def update_item(
    id: int,
    body: ItemUpdate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[ItemOut]:
    data = await item_service.update_item(request_context, id, body)
    return SingleObjectResponse(data=data)


# =========================================================
# DELETE routes
# =========================================================

@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["delete_item"],
    summary=SUMMARIES["delete_item"],
    description=DOCSTRINGS["delete_item"],
)
async def delete_item(
    id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> None:
    return await item_service.delete_item(request_context, id)
