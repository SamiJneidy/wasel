from math import ceil
from fastapi import APIRouter, status
from typing import Annotated

from src.core.dependencies.shared import get_current_user
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)

from src.users.schemas import UserInDB
from src.docs.invoices import RESPONSES, DOCSTRINGS, SUMMARIES

from .dependencies.full_service import Depends, get_invoice_service
from .schemas import (
    GetInvoiceNumberRequest,
    GetInvoiceNumberResponse,
    SaleInvoiceFilters,
    SaleInvoiceHeaderOut,
    SaleInvoiceUpdate,
    SaleInvoiceCreate,
    SaleInvoiceOut,
)
from src.core.enums import DocumentType

from .services.full_service import SaleInvoiceService

router = APIRouter(
    prefix="/sale-invoices",
    tags=["Sale Invoices"],
)

# =========================================================
# GET routes
# =========================================================

@router.get(
    path="",
    response_model=PaginatedResponse[SaleInvoiceOut],
)
async def get_invoices(
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    pagination: PagintationParams = Depends(),
    filters: SaleInvoiceFilters = Depends(),
) -> PaginatedResponse[SaleInvoiceOut]:
    from datetime import datetime
    total_rows, data = await invoice_service.get_invoices(current_user, pagination, filters)
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=ceil(total_rows / pagination.limit) if pagination.limit else 1,
        page=pagination.page,
        limit=pagination.limit,
    )

@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[SaleInvoiceOut],
    responses=RESPONSES["get_invoice"],
    summary=SUMMARIES["get_invoice"],
    description=DOCSTRINGS["get_invoice"],
)
async def get_invoice(
    id: int,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:

    data = await invoice_service.get_invoice(current_user, id)
    return SingleObjectResponse(data=data)


# =========================================================
# POST routes
# =========================================================

@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[SaleInvoiceOut],
    responses=RESPONSES["create_invoice"],
    summary=SUMMARIES["create_invoice"],
    description=DOCSTRINGS["create_invoice"],
)
async def create_invoice(
    body: SaleInvoiceCreate,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:
    data = await invoice_service.create_invoice(current_user, body)
    return SingleObjectResponse(data=data)


@router.post(
    path="/generate-invoice-number",
    response_model=SingleObjectResponse[GetInvoiceNumberResponse],
    responses=RESPONSES["generate_invoice_number"],
    summary=SUMMARIES["generate_invoice_number"],
    description=DOCSTRINGS["generate_invoice_number"],
)
async def generate_invoice_number(
    data: GetInvoiceNumberRequest,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[GetInvoiceNumberResponse]:
    seq_number, invoice_number = await invoice_service.generate_invoice_number(
        current_user,
        data.document_type,
        data.invoice_type,
        data.invoice_type_code,
    )
    return SingleObjectResponse(data=GetInvoiceNumberResponse(invoice_number=invoice_number))


@router.post(
    path="/convert/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SingleObjectResponse[SaleInvoiceOut],
    responses=RESPONSES["create_invoice"],
    summary=SUMMARIES["create_invoice"],
    description=DOCSTRINGS["create_invoice"],
)
async def convert_invoice(
    id: int,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:

    data = await invoice_service.convert_quotation_to_invoice(current_user, id)
    return SingleObjectResponse(data=data)

@router.post(
    path="/submit/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SingleObjectResponse[SaleInvoiceOut],
    responses=RESPONSES["create_invoice"],
    summary=SUMMARIES["create_invoice"],
    description=DOCSTRINGS["create_invoice"],
)
async def submit_invoice_to_tax_authority(
    id: int,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:
    data = await invoice_service.submit_invoice_to_tax_authority(current_user, id)
    return SingleObjectResponse(data=data)

# =========================================================
# PUT routes
# =========================================================

@router.put(
    path="/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SingleObjectResponse[SaleInvoiceOut],
    responses=RESPONSES["create_invoice"],
    summary=SUMMARIES["create_invoice"],
    description=DOCSTRINGS["create_invoice"],
)
async def update_invoice(
    id: int,
    body: SaleInvoiceUpdate,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:
    data = await invoice_service.update_invoice(current_user, id, body)
    return SingleObjectResponse(data=data)


# =========================================================
# DELETE routes
# =========================================================

@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["create_invoice"],
    summary=SUMMARIES["create_invoice"],
    description=DOCSTRINGS["create_invoice"],
)
async def delete_invoice(
    id: int,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> None:

    await invoice_service.delete_invoice(current_user, id)
