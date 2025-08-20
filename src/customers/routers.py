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
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.create(body)
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
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.update(id, body)
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
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    return await customer_service.delete(id)


@router.get(
    path="/",
    response_model=ObjectListResponse[CustomerOut],
    responses=RESPONSES["get_customers_for_user"],
    summary=SUMMARIES["get_customers_for_user"],
    description=DOCSTRINGS["get_customers_for_user"],
)
async def get_customers_for_user(
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ObjectListResponse[CustomerOut]:
    data = await customer_service.get_customers_for_user()
    return ObjectListResponse(data=data)


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
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[CustomerOut]:
    data = await customer_service.get(id)
    return SingleObjectResponse(data=data)