from math import ceil
from fastapi import APIRouter, status

from src.users.dependencies import UserService, get_user_service
from .services import CustomerService
from .schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
    UserOut,
    ObjectListResponse,
    SingleObjectResponse,
    PagintationParams,
    PaginatedResponse,
    CustomerFilters,
)
from .dependencies import (
    Annotated,
    Depends,
    get_customer_service,
    get_current_user,
)
from src.docs.customers import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[CustomerOut],
    responses=RESPONSES["create_customer"],
    summary=SUMMARIES["create_customer"],
    description=DOCSTRINGS["create_customer"],
)
async def create_customer(
    body: CustomerCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_email: Annotated[str, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    current_user = await user_service.get_by_email(current_user_email)
    data = await customer_service.create(current_user.id, body)
    return SingleObjectResponse(data=data)


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
    user_service: Annotated[UserService, Depends(get_user_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_email: Annotated[str, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    current_user = await user_service.get_by_email(current_user_email)
    data = await customer_service.update(current_user.id, id, body)
    return SingleObjectResponse(data=data)


@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["delete_customer"],
    summary=SUMMARIES["delete_customer"],
    description=DOCSTRINGS["delete_customer"],
)
async def delete_customer(
    id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_email: Annotated[str, Depends(get_current_user)],
) -> None:
    current_user = await user_service.get_by_email(current_user_email)
    return await customer_service.delete(current_user.id, id)


@router.get(
    path="",
    response_model=PaginatedResponse[CustomerOut],
    responses=RESPONSES["get_customers_for_user"],
    summary=SUMMARIES["get_customers_for_user"],
    description=DOCSTRINGS["get_customers_for_user"],
)
async def get_customers_for_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_email: Annotated[str, Depends(get_current_user)],
    pagination_params: PagintationParams = Depends(),
    filters: CustomerFilters = Depends(),
) -> PaginatedResponse[CustomerOut]:
    current_user = await user_service.get_by_email(current_user_email)
    total_rows, data = await customer_service.get_customers_for_user(current_user.id, pagination_params, filters)
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=ceil(total_rows/pagination_params.limit) if pagination_params.limit is not None else 1,
        page=pagination_params.page,
        limit=pagination_params.limit
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
    user_service: Annotated[UserService, Depends(get_user_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_email: Annotated[str, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    current_user = await user_service.get_by_email(current_user_email)
    data = await customer_service.get(current_user.id, id)
    return SingleObjectResponse(data=data)