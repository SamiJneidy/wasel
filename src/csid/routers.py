from fastapi import APIRouter, status

from .services import CSIDService
from .schemas import (
    ComplianceCSIDRequest,
    CSIDOut,
    UserOut,
    SuccessfulResponse
)
from .dependencies import (
    Annotated,
    Depends, 
    get_csid_service,
    get_current_user,
)
from src.docs.csid import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/csid", 
    tags=["CSID"],
)


@router.post(
    path="/compliance",
    response_model=CSIDOut,
    responses=RESPONSES["generate_compliance_csid"],
    summary=SUMMARIES["generate_compliance_csid"],
    description=DOCSTRINGS["generate_compliance_csid"],
)
async def generate_compliance_csid(
    body: ComplianceCSIDRequest,
    csid_service: Annotated[CSIDService, Depends(get_csid_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> CSIDOut:
    return await csid_service.generate_compliance_csid(current_user.email, body)



@router.post(
    path="/production",
    response_model=CSIDOut,
    responses=RESPONSES["generate_production_csid"],
    summary=SUMMARIES["generate_production_csid"],
    description=DOCSTRINGS["generate_production_csid"],
)
async def generate_production_csid(
    csid_service: Annotated[CSIDService, Depends(get_csid_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> CSIDOut:
    return await csid_service.generate_production_csid(current_user.email)

