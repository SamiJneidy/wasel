from math import ceil
from fastapi import APIRouter, status
from src.core.enums import Stage, InvoiceType
from .services import InvoiceService
from .schemas import (
    InvoiceFilters,
    SingleObjectResponse,
    SuccessfulResponse,
    InvoiceCreate,
    InvoiceOut,
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
    prefix="/invoices", 
    tags=["Invoices"],
)


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[InvoiceOut],
    responses=RESPONSES["create_invoice"],
    summary=SUMMARIES["create_invoice"],
    description=DOCSTRINGS["create_invoice"],
)
async def create_invoice(
    body: InvoiceCreate,
    invoice_service: Annotated[InvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[InvoiceOut]:
    if current_user.stage == Stage.COMPLIANCE:
        data = await invoice_service.create_compliance_invoice(body)
    elif body.invoice_type == InvoiceType.STANDARD:
        data = await invoice_service.create_standard_invoice(body)
    elif body.invoice_type == InvoiceType.SIMPLIFIED:
        data = await invoice_service.create_simplified_invoice(body)
    return SingleObjectResponse(data=data)



@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[InvoiceOut],
    responses=RESPONSES["get_invoice"],
    summary=SUMMARIES["get_invoice"],
    description=DOCSTRINGS["get_invoice"],
)
async def get_invoice(
    id: int,
    invoice_service: Annotated[InvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[InvoiceOut]:
    invoice = await invoice_service.get_invoice(id)
    return SingleObjectResponse(data=invoice)

@router.get(
    path="/",
    response_model=PaginatedResponse[InvoiceOut],
    # responses=RESPONSES["get_invoices"],
    # summary=SUMMARIES["get_invoices"],
    # description=DOCSTRINGS["get_invoices"],
)
async def get_invoices(
    pagination: PagintationParams = Depends(),
    filters: InvoiceFilters = Depends(),
    current_user: UserOut = Depends(get_current_user),
    invoice_service: InvoiceService = Depends(get_invoice_service),
) -> PaginatedResponse[InvoiceOut]:
    total_rows, data = await invoice_service.get_invoices(pagination, filters)
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=ceil(total_rows/pagination.limit) if pagination.limit is not None else 1,
        page=pagination.page,
        limit=pagination.limit
    )
