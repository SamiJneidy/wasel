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

router = APIRouter(
    prefix="/invoices", 
    tags=["Invoices"],
)


@router.post(
    path="/",
    response_model=SingleObjectResponse[InvoiceOut],
    responses={
        status.HTTP_200_OK: {
            "description": "User was returned successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UesrNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def create_invoice(
    body: InvoiceCreate,
    invoice_service: Annotated[InvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[InvoiceOut]:
    """Create a new invoice."""
    if current_user.stage == Stage.COMPLIANCE:
        data = await invoice_service.create_compliance_invoice(body)
    elif body.invoice_type == InvoiceType.STANDARD:
        data = await invoice_service.create_standard_invoice(body)
    elif body.invoice_type == InvoiceType.SIMPLIFIED:
        data = await invoice_service.create_simplified_invoice(body)
    return SingleObjectResponse(data=data)


@router.post(
    path="/switch-to-production",
    response_model=SuccessfulResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "User was returned successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UesrNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def switch_to_production(
    invoice_service: Annotated[InvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SuccessfulResponse:
    await invoice_service.switch_to_production()
    return SuccessfulResponse(detail="Success. You are now running on production stage")



from pydantic import BaseModel
class Ex(BaseModel):
    detail: str

@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[InvoiceOut],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "model": Ex
        }
    }
)
async def get_invoice(
    id: int,
    invoice_service: Annotated[InvoiceService, Depends(get_invoice_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[InvoiceOut]:
    """Get invoice."""
    invoice = await invoice_service.get_invoice(id)
    return SingleObjectResponse(data=invoice)
