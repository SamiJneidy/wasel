from math import ceil

from fastapi import APIRouter, status

from src.core.dependencies.shared import get_current_user
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
from src.docs.items import DOCSTRINGS, RESPONSES, SUMMARIES
from src.users.schemas import UserInDB

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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    pagination_params: PagintationParams = Depends(),
    filters: ItemFilters = Depends(),
) -> PaginatedResponse[ItemOut]:
    total_rows, data = await item_service.get_items(
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
    response_model=SingleObjectResponse[ItemOut],
    responses=RESPONSES["get_item"],
    summary=SUMMARIES["get_item"],
    description=DOCSTRINGS["get_item"],
)
async def get_item(
    id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[ItemOut]:
    data = await item_service.get(current_user, id)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[ItemOut]:
    data = await item_service.create(current_user, body)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[ItemOut]:
    data = await item_service.update(current_user, id, body)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> None:
    return await item_service.delete(current_user, id)
