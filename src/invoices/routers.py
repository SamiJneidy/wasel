from fastapi import APIRouter, status
from src.core.enums import Stage, InvoiceType
from .services import InvoiceService
from .schemas import (
    SingleObjectResponse,
    SuccessfulResponse,
    InvoiceCreate,
    InvoiceOut,
    UserOut,
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
