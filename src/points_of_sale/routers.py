from fastapi import APIRouter, status

from src.core.dependencies.auth import get_request_context
from src.core.utils.math_helper import calc_total_pages
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
# from src.docs.points_of_sale import DOCSTRINGS, RESPONSES, SUMMARIES

from .dependencies import Annotated, Depends, get_point_of_sale_service
from .schemas import PointOfSaleCreate, PointOfSaleFilters, PointOfSaleOut, PointOfSaleUpdate
from .services import PointOfSaleService
from src.core.schemas.context import RequestContext

router = APIRouter(
    prefix="/points-of-sale",
    tags=["Points Of Sale"],
)


# =========================================================
# GET routes
# =========================================================

@router.get(
    path="",
    response_model=PaginatedResponse[PointOfSaleOut],
    # responses=RESPONSES["get_points_of_sale_for_user"],
    # summary=SUMMARIES["get_points_of_sale_for_user"],
    # description=DOCSTRINGS["get_points_of_sale_for_user"],
)
async def get_points_of_sale(
    point_of_sale_service: Annotated[PointOfSaleService, Depends(get_point_of_sale_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    pagination_params: PagintationParams = Depends(),
    filters: PointOfSaleFilters = Depends(),
) -> PaginatedResponse[PointOfSaleOut]:
    total_rows, data = await point_of_sale_service.get_points_of_sale(request_context, pagination_params, filters)
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=calc_total_pages(total_rows, pagination_params.limit),
        page=pagination_params.page,
        limit=pagination_params.limit,
    )


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[PointOfSaleOut],
    # responses=RESPONSES["get_point_of_sale"],
    # summary=SUMMARIES["get_point_of_sale"],
    # description=DOCSTRINGS["get_point_of_sale"],
)
async def get_point_of_sale(
    id: int,
    point_of_sale_service: Annotated[PointOfSaleService, Depends(get_point_of_sale_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[PointOfSaleOut]:
    data = await point_of_sale_service.get_point_of_sale(request_context, id)
    return SingleObjectResponse(data=data)


# =========================================================
# POST routes
# =========================================================

@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[PointOfSaleOut],
    # responses=RESPONSES["create_point_of_sale"],
    # summary=SUMMARIES["create_point_of_sale"],
    # description=DOCSTRINGS["create_point_of_sale"],
)
async def create_point_of_sale(
    body: PointOfSaleCreate,
    point_of_sale_service: Annotated[PointOfSaleService, Depends(get_point_of_sale_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[PointOfSaleOut]:
    data = await point_of_sale_service.create_point_of_sale(request_context, body)
    return SingleObjectResponse(data=data)


# =========================================================
# PATCH routes
# =========================================================

@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[PointOfSaleOut],
    # responses=RESPONSES["update_point_of_sale"],
    # summary=SUMMARIES["update_point_of_sale"],
    # description=DOCSTRINGS["update_point_of_sale"],
)
async def update_point_of_sale(
    id: int,
    body: PointOfSaleUpdate,
    point_of_sale_service: Annotated[PointOfSaleService, Depends(get_point_of_sale_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[PointOfSaleOut]:
    data = await point_of_sale_service.update_point_of_sale(request_context, id, body)
    return SingleObjectResponse(data=data)


# =========================================================
# DELETE routes
# =========================================================

@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # responses=RESPONSES["delete_point_of_sale"],
    # summary=SUMMARIES["delete_point_of_sale"],
    # description=DOCSTRINGS["delete_point_of_sale"],
)
async def delete_point_of_sale(
    id: int,
    point_of_sale_service: Annotated[PointOfSaleService, Depends(get_point_of_sale_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> None:
    return await point_of_sale_service.delete_point_of_sale(request_context, id)
