from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from .repositories import CSIDRepository, InvoiceRepository
from .services import CSIDService
from src.zatca.dependencies import get_zatca_service, ZatcaService
from src.users.dependencies import get_user_service, UserService
from src.invoices.repositories import InvoiceRepository
from src.auth.dependencies import get_current_user
from src.core.database import get_db


def get_csid_repository(db: Annotated[Session, Depends(get_db)]) -> CSIDRepository:
    return CSIDRepository(db)

def get_csid_service(
    db: Annotated[Session, Depends(get_db)],
    csid_repo: Annotated[CSIDRepository, Depends(get_csid_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    zatca_service: Annotated[ZatcaService, Depends(get_zatca_service)],
) -> CSIDService:
    
    return CSIDService(csid_repo, user_service, zatca_service, InvoiceRepository(db))
