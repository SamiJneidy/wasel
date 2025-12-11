from math import ceil

from fastapi import APIRouter, status

from src.core.dependencies.shared import get_current_user
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
from src.users.schemas import UserInDB
from src.docs.invoices import RESPONSES, DOCSTRINGS, SUMMARIES

from .dependencies import Annotated, Depends, get_invoice_service
from .schemas import (
    BuyInvoiceCreate,
    BuyInvoiceFilters,
    BuyInvoiceOut,
)
from .services import BuyInvoiceService

router = APIRouter(
    prefix="/buy-invoices",
    tags=["Buy Invoices"],
)

# =========================================================
# POST routes
# =========================================================

@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[BuyInvoiceOut],
    # responses=RESPONSES["create_invoice"],
    # summary=SUMMARIES["create_invoice"],
    # description=DOCSTRINGS["create_invoice"],
)
async def create_invoice(
    body: BuyInvoiceCreate,
    invoice_service: Annotated[BuyInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[BuyInvoiceOut]:
    from datetime import datetime
    start = datetime.now()
    data = await invoice_service.create_buy_invoice(current_user, body)
    end = datetime.now()
    print((end-start).seconds)
    return SingleObjectResponse(data=data)


# =========================================================
# GET routes
# =========================================================

@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[BuyInvoiceOut],
    # responses=RESPONSES["get_invoice"],
    # summary=SUMMARIES["get_invoice"],
    # description=DOCSTRINGS["get_invoice"],
)
async def get_invoice(
    id: int,
    invoice_service: Annotated[BuyInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[BuyInvoiceOut]:
    data = await invoice_service.get_invoice(current_user, id)
    return SingleObjectResponse(data=data)


@router.get(
    path="",
    response_model=PaginatedResponse[BuyInvoiceOut],
    # responses=RESPONSES["get_invoices"],
    # summary=SUMMARIES["get_invoices"],
    # description=DOCSTRINGS["get_invoices"],
)
async def get_invoices(
    invoice_service: Annotated[BuyInvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    pagination: PagintationParams = Depends(),
    filters: BuyInvoiceFilters = Depends(),
) -> PaginatedResponse[BuyInvoiceOut]:
    total_rows, data = await invoice_service.get_invoices(
        current_user,
        pagination,
        filters,
    )
    return PaginatedResponse(
        data=data,
        total_rows=total_rows,
        total_pages=(
            ceil(total_rows / pagination.limit)
            if pagination.limit is not None
            else 1
        ),
        page=pagination.page,
        limit=pagination.limit,
    )
