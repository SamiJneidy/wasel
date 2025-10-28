from math import ceil
from fastapi import APIRouter, status
from src.core.enums import Stage
from .services import SaleInvoiceService
from .schemas import (
    GetInvoiceNumberRequest,
    GetInvoiceNumberResponse,
    SaleInvoiceFilters,
    SaleInvoiceUpdate,
    SingleObjectResponse,
    SuccessfulResponse,
    SaleInvoiceCreate,
    SaleInvoiceOut,
    UserOut,
    PagintationParams,
    PaginatedResponse
)
from .dependencies import (
    Annotated,
    Depends, 
    get_invoice_service,
    get_current_user,
)
from src.docs.invoices import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/sale-invoices", 
    tags=["Sale Invoices"],
)


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[SaleInvoiceOut],
    responses=RESPONSES["create_invoice"],
    summary=SUMMARIES["create_invoice"],
    description=DOCSTRINGS["create_invoice"],
)
async def create_invoice(
    body: SaleInvoiceCreate,
    invoice_service: Annotated[SaleInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:
    data = await invoice_service.create_invoice(body)
    return SingleObjectResponse(data=data)


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
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:
    data = await invoice_service.update_invoice(id, body)
    return SingleObjectResponse(data=data)


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
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    await invoice_service.delete_invoice(id)


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
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:
    invoice = await invoice_service.get_invoice(id)
    return SingleObjectResponse(data=invoice)


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
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SaleInvoiceOut]:
    seq_number, invoice_number = await invoice_service.generate_invoice_number(current_user.id, data.invoice_type, data.invoice_type_code)
    return SingleObjectResponse(data=GetInvoiceNumberResponse(invoice_number=invoice_number))


@router.get(
    path="/",
    response_model=PaginatedResponse[SaleInvoiceOut],
    # responses=RESPONSES["get_invoices"],
    # summary=SUMMARIES["get_invoices"],
    # description=DOCSTRINGS["get_invoices"],
)
async def get_invoices(
    pagination: PagintationParams = Depends(),
    filters: SaleInvoiceFilters = Depends(),
    current_user: UserOut = Depends(get_current_user),
    invoice_service: SaleInvoiceService = Depends(get_invoice_service),
) -> PaginatedResponse[SaleInvoiceOut]:
    total_rows, data = await invoice_service.get_invoices(pagination, filters)
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=ceil(total_rows/pagination.limit) if pagination.limit is not None else 1,
        page=pagination.page,
        limit=pagination.limit
    )
