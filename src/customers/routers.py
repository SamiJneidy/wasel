from fastapi import APIRouter, status
from .services import CustomerService
from .schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
    UserOut,
    ObjectListResponse,
    SingleObjectResponse,
)
from .dependencies import (
    Annotated,
    Depends,
    get_customer_service,
    get_current_user,
)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post(
    path="/",
    response_model=SingleObjectResponse[CustomerOut],
)
async def create_customer(
    body: CustomerCreate,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> CustomerOut:
    """Create a new customer."""
    data = await customer_service.create(body)
    return SingleObjectResponse(data=data)


@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[CustomerOut],
)
async def update_customer(
    id: int,
    body: CustomerUpdate,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> CustomerOut:
    """Update a customer."""
    data = await customer_service.update(id, body)
    return SingleObjectResponse(data=data)


@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer(
    id: int,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    """Delete a customer."""
    return await customer_service.delete(id)


@router.get(
    path="/",
    response_model=ObjectListResponse[CustomerOut],
)
async def get_customers_for_user(
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ObjectListResponse[CustomerOut]:
    """Delete a customer."""
    data = await customer_service.get_customers_for_user()
    return ObjectListResponse(data=data)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[CustomerOut]
)
async def get_customer(
    id: int,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> CustomerOut:
    """Get a signle customer."""
    data = await customer_service.get(id)
    return SingleObjectResponse(data=data)