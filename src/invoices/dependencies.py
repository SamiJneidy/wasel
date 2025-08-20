from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from .repositories import InvoiceRepository
from .schemas import UserOut
from .services import InvoiceService
from src.zatca.dependencies import get_zatca_service, ZatcaService
from src.csid.dependencies import get_csid_service, CSIDService
from src.customers.dependencies import get_customer_service, CustomerService
from src.items.dependencies import get_item_service, ItemService
from src.users.dependencies import get_user_service, UserService
from src.auth.dependencies import get_current_user
from src.core.database import get_db

def get_invoice_repository(db: Annotated[Session, Depends(get_db)]) -> InvoiceRepository:
    return InvoiceRepository(db)

def get_invoice_service(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserOut, Depends(get_current_user)],
    csid_service: Annotated[CSIDService, Depends(get_csid_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
    zatca_service: Annotated[ZatcaService, Depends(get_zatca_service)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> InvoiceService:
    return InvoiceService(db, user, csid_service, customer_service, item_service, zatca_service, user_service, InvoiceRepository(db))
