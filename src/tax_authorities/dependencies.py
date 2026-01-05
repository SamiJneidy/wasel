from fastapi import Depends
from typing import Annotated
from .services import TaxAuthorityService
from src.core.enums import TaxAuthority
from src.core.database import get_db
from src.core.dependencies.shared import UserInDB, get_current_user
from .zatca_phase2.dependencies import ZatcaPhase2Service, get_zatca_phase2_service
from .no_tax_authority.dependencies import NoTaxAuthorityService, get_no_tax_authority_service

def get_tax_authority_service(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    no_tax_authority_service: Annotated[NoTaxAuthorityService, Depends(get_no_tax_authority_service)],
    zatca_phase2_service: Annotated[ZatcaPhase2Service, Depends(get_zatca_phase2_service)],
) -> TaxAuthorityService:
    if current_user.organization.tax_authority is None:
        return no_tax_authority_service
    if current_user.organization.tax_authority == TaxAuthority.ZATCA_PHASE2:
        return zatca_phase2_service
