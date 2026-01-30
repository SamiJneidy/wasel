from fastapi import APIRouter, status

from src.core.dependencies.auth import get_request_context
from src.core.utils.math_helper import calc_total_pages
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
from src.docs.customers import DOCSTRINGS, RESPONSES, SUMMARIES
from src.core.schemas.context import RequestContext

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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    pagination_params: PagintationParams = Depends(),
    filters: CustomerFilters = Depends(),
) -> PaginatedResponse[CustomerOut]:
    total_rows, data = await customer_service.get_customers(
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
    response_model=SingleObjectResponse[CustomerOut],
    responses=RESPONSES["get_customer"],
    summary=SUMMARIES["get_customer"],
    description=DOCSTRINGS["get_customer"],
)
async def get_customer(
    id: int,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.get_customer(request_context, id)
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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.create_customer(request_context, body)
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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.update_customer(request_context, id, body)
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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> None:
    return await customer_service.delete_customer(request_context, id)
