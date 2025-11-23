from math import ceil

from fastapi import APIRouter, status

from src.core.dependencies.shared import get_current_user
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
from src.docs.customers import DOCSTRINGS, RESPONSES, SUMMARIES
from src.users.schemas import UserInDB

from .dependencies import Annotated, Depends, get_customer_service
from .schemas import CustomerCreate, CustomerFilters, CustomerOut, CustomerUpdate
from .services import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


# =========================================================
# GET routes
# =========================================================

@router.get(
    path="",
    response_model=PaginatedResponse[CustomerOut],
    responses=RESPONSES["get_customers_for_user"],
    summary=SUMMARIES["get_customers_for_user"],
    description=DOCSTRINGS["get_customers_for_user"],
)
async def get_customers_for_user(
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    pagination_params: PagintationParams = Depends(),
    filters: CustomerFilters = Depends(),
) -> PaginatedResponse[CustomerOut]:
    total_rows, data = await customer_service.get_customers_for_user(
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
    response_model=SingleObjectResponse[CustomerOut],
    responses=RESPONSES["get_customer"],
    summary=SUMMARIES["get_customer"],
    description=DOCSTRINGS["get_customer"],
)
async def get_customer(
    id: int,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.get(current_user, id)
    return SingleObjectResponse(data=data)


# =========================================================
# POST routes
# =========================================================

@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[CustomerOut],
    responses=RESPONSES["create_customer"],
    summary=SUMMARIES["create_customer"],
    description=DOCSTRINGS["create_customer"],
)
async def create_customer(
    body: CustomerCreate,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.create(current_user, body)
    return SingleObjectResponse(data=data)


# =========================================================
# PATCH routes
# =========================================================

@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[CustomerOut],
    responses=RESPONSES["update_customer"],
    summary=SUMMARIES["update_customer"],
    description=DOCSTRINGS["update_customer"],
)
async def update_customer(
    id: int,
    body: CustomerUpdate,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.update(current_user, id, body)
    return SingleObjectResponse(data=data)


# =========================================================
# DELETE routes
# =========================================================

@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["delete_customer"],
    summary=SUMMARIES["delete_customer"],
    description=DOCSTRINGS["delete_customer"],
)
async def delete_customer(
    id: int,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> None:
    return await customer_service.delete(current_user, id)
