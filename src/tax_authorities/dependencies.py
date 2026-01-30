from fastapi import Depends
from typing import Annotated
from .services import TaxAuthorityService
from src.core.enums import TaxAuthority
from src.core.database import get_db
from src.core.dependencies.auth import RequestContext, get_request_context
from .zatca_phase2.dependencies import ZatcaPhase2Service, get_zatca_phase2_service
from .no_tax_authority.dependencies import NoTaxAuthorityService, get_no_tax_authority_service
from .zatca_phase1.dependencies import ZatcaPhase1Service, get_zatca_phase1_service

def get_tax_authority_service(
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    no_tax_authority_service: Annotated[NoTaxAuthorityService, Depends(get_no_tax_authority_service)],
    zatca_phase2_service: Annotated[ZatcaPhase2Service, Depends(get_zatca_phase2_service)],
    zatca_phase1_service: Annotated[ZatcaPhase1Service, Depends(get_zatca_phase1_service)],
) -> TaxAuthorityService:
    if request_context.organization.tax_authority is None:
        return no_tax_authority_service
    if request_context.organization.tax_authority == TaxAuthority.ZATCA_PHASE1:
        return zatca_phase1_service
    if request_context.organization.tax_authority == TaxAuthority.ZATCA_PHASE2:
        return zatca_phase2_service
