from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from .repositories import BuyInvoiceRepository
from .schemas import UserOut
from .services import BuyInvoiceService
from src.zatca.dependencies import get_zatca_service, ZatcaService
from src.csid.dependencies import get_csid_service, CSIDService
from src.suppliers.dependencies import get_supplier_service, SupplierService
from src.items.dependencies import get_item_service, ItemService
from src.users.dependencies import get_user_service, UserService
from src.auth.dependencies import get_current_user
from src.core.database import get_db

def get_invoice_repository(db: Annotated[Session, Depends(get_db)]) -> BuyInvoiceRepository:
    return BuyInvoiceRepository(db)

def get_invoice_service(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserOut, Depends(get_current_user)],
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> BuyInvoiceService:
    return BuyInvoiceService(db, user, supplier_service, item_service, user_service, BuyInvoiceRepository(db))
