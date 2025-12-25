from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db

from .repositories import SaleInvoiceRepository
from .services import SaleInvoiceService

from src.customers.dependencies import get_customer_service, CustomerService
from src.items.dependencies import get_item_service, ItemService
from src.core.services.compliance_service import ComplianceService
from src.zatca.dependencies import get_zatca_service


async def get_sale_invoice_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SaleInvoiceRepository:
    return SaleInvoiceRepository(db)

async def get_invoice_service(
    repo: Annotated[SaleInvoiceRepository, Depends(get_sale_invoice_repository)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
    compliance_service: Annotated[ComplianceService, Depends(get_compliance_service)],
) -> SaleInvoiceService:

    return SaleInvoiceService(
        repo=repo,
        customer_service=customer_service,
        item_service=item_service,
        compliance_service=compliance_service,
    )
