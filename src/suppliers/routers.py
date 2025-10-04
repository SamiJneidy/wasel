from fastapi import APIRouter, status
from .services import SupplierService
from .schemas import (
    SupplierCreate,
    SupplierUpdate,
    SupplierOut,
    UserOut,
    ObjectListResponse,
    SingleObjectResponse,
)
from .dependencies import (
    Annotated,
    Depends,
    get_supplier_service,
    get_current_user,
)
from src.docs.suppliers import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[SupplierOut],
    responses=RESPONSES["create_supplier"],
    summary=SUMMARIES["create_supplier"],
    description=DOCSTRINGS["create_supplier"],
)
async def create_supplier(
    body: SupplierCreate,
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SupplierOut]:
    data = await supplier_service.create(body)
    return SingleObjectResponse(data=data)


@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[SupplierOut],
    responses=RESPONSES["update_supplier"],
    summary=SUMMARIES["update_supplier"],
    description=DOCSTRINGS["update_supplier"],
)
async def update_supplier(
    id: int,
    body: SupplierUpdate,
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SupplierOut]:
    data = await supplier_service.update(id, body)
    return SingleObjectResponse(data=data)


@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["delete_supplier"],
    summary=SUMMARIES["delete_supplier"],
    description=DOCSTRINGS["delete_supplier"],
)
async def delete_supplier(
    id: int,
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    return await supplier_service.delete(id)


@router.get(
    path="/",
    response_model=ObjectListResponse[SupplierOut],
    responses=RESPONSES["get_suppliers_for_user"],
    summary=SUMMARIES["get_suppliers_for_user"],
    description=DOCSTRINGS["get_suppliers_for_user"],
)
async def get_suppliers_for_user(
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ObjectListResponse[SupplierOut]:
    data = await supplier_service.get_suppliers_for_user()
    return ObjectListResponse(data=data)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[SupplierOut],
    responses=RESPONSES["get_supplier"],
    summary=SUMMARIES["get_supplier"],
    description=DOCSTRINGS["get_supplier"],
)
async def get_supplier(
    id: int,
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SupplierOut]:
    data = await supplier_service.get(id)
    return SingleObjectResponse(data=data)