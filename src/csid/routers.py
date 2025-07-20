from fastapi import APIRouter, status
from .services import CSIDService
from .schemas import (
    ComplianceCSIDRequest,
    ComplianceCSIDResponse,
    UserOut,
)
from .dependencies import (
    Annotated,
    Depends, 
    get_csid_service,
    get_current_user,
)

router = APIRouter(
    prefix="/csid", 
    tags=["CSID"],
)


@router.post(
    path="/compliance",
    response_model=ComplianceCSIDResponse,
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
async def generate_compliance_csid(
    body: ComplianceCSIDRequest,
    csid_service: Annotated[CSIDService, Depends(get_csid_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ComplianceCSIDResponse:
    """Generate a compliance CSID."""
    return await csid_service.generate_compliance_csid(current_user.email, body)
