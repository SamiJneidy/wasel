from fastapi import APIRouter, status

from src.core.dependencies.auth import get_request_context
from src.core.schemas.context import RequestContext
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
from src.core.utils.math_helper import calc_total_pages
from src.docs.suppliers import DOCSTRINGS, RESPONSES, SUMMARIES

from .dependencies import Annotated, Depends, get_supplier_service
from .schemas import SupplierCreate, SupplierFilters, SupplierOut, SupplierUpdate
from .services import SupplierService

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


# =========================================================
# GET routes
# =========================================================

@router.get(
    path="",
    response_model=PaginatedResponse[SupplierOut],
    responses=RESPONSES["get_suppliers_for_user"],
    summary=SUMMARIES["get_suppliers_for_user"],
    description=DOCSTRINGS["get_suppliers_for_user"],
)
async def get_suppliers_for_user(
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    pagination_params: PagintationParams = Depends(),
    filters: SupplierFilters = Depends(),
) -> PaginatedResponse[SupplierOut]:
    total_rows, data = await supplier_service.get_suppliers(
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
    response_model=SingleObjectResponse[SupplierOut],
    responses=RESPONSES["get_supplier"],
    summary=SUMMARIES["get_supplier"],
    description=DOCSTRINGS["get_supplier"],
)
async def get_supplier(
    id: int,
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[SupplierOut]:
    data = await supplier_service.get_supplier(request_context, id)
    return SingleObjectResponse(data=data)


# =========================================================
# POST routes
# =========================================================

@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[SupplierOut],
    responses=RESPONSES["create_supplier"],
    summary=SUMMARIES["create_supplier"],
    description=DOCSTRINGS["create_supplier"],
)
async def create_supplier(
    body: SupplierCreate,
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[SupplierOut]:
    data = await supplier_service.create_supplier(request_context, body)
    return SingleObjectResponse(data=data)


# =========================================================
# PATCH routes
# =========================================================

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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> SingleObjectResponse[SupplierOut]:
    data = await supplier_service.update_supplier(request_context, id, body)
    return SingleObjectResponse(data=data)


# =========================================================
# DELETE routes
# =========================================================

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
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> None:
    return await supplier_service.delete_supplier(request_context, id)
