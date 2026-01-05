from fastapi import Depends
from typing import Annotated
from .services import ZatcaPhase2Service
from src.core.services import AsyncRequestService
from src.core.dependencies.requests_deps import get_requests_service
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import ZatcaRepository
from .services import ZatcaPhase2Service
from src.core.database import get_db
from src.items.dependencies import get_item_service, ItemService
from src.customers.dependencies import get_customer_service, CustomerService
from src.sale_invoices.dependencies.raw_service import get_invoice_service, SaleInvoiceServiceRaw
def get_zatca_phase2_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ZatcaRepository:
    return ZatcaRepository(db)


def get_zatca_phase2_service(
    repo: Annotated[ZatcaRepository, Depends(get_zatca_phase2_repository)],
    requests_service: Annotated[AsyncRequestService, Depends(get_requests_service)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    sale_invoice_service: Annotated[SaleInvoiceServiceRaw, Depends(get_invoice_service)],
) -> ZatcaPhase2Service:
    return ZatcaPhase2Service(repo, requests_service, item_service, customer_service, sale_invoice_service)