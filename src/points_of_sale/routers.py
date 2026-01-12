from math import ceil

from fastapi import APIRouter, status

from src.core.dependencies.shared import get_current_user
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
# from src.docs.points_of_sale import DOCSTRINGS, RESPONSES, SUMMARIES
from src.users.schemas import UserInDB

from .dependencies import Annotated, Depends, get_point_of_sale_service
from .schemas import PointOfSaleCreate, PointOfSaleFilters, PointOfSaleOut, PointOfSaleUpdate
from .services import PointOfSaleService

router = APIRouter(
    prefix="/points_of_sale",
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    pagination_params: PagintationParams = Depends(),
    filters: PointOfSaleFilters = Depends(),
) -> PaginatedResponse[PointOfSaleOut]:
    total_rows, data = await point_of_sale_service.get_points_of_sale(
        current_user,
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
    response_model=SingleObjectResponse[PointOfSaleOut],
    # responses=RESPONSES["get_point_of_sale"],
    # summary=SUMMARIES["get_point_of_sale"],
    # description=DOCSTRINGS["get_point_of_sale"],
)
async def get_point_of_sale(
    id: int,
    point_of_sale_service: Annotated[PointOfSaleService, Depends(get_point_of_sale_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[PointOfSaleOut]:
    data = await point_of_sale_service.get(current_user, id)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[PointOfSaleOut]:
    data = await point_of_sale_service.create(current_user, body)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[PointOfSaleOut]:
    data = await point_of_sale_service.update(current_user, id, body)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> None:
    return await point_of_sale_service.delete(current_user, id)
