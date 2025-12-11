from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from .repositories import BuyInvoiceRepository
from .services import BuyInvoiceService
from src.suppliers.dependencies import get_supplier_service, SupplierService
from src.items.dependencies import get_item_service, ItemService


async def get_buy_invoice_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BuyInvoiceRepository:
    return BuyInvoiceRepository(db)


def get_invoice_service(
    buy_invoice_repository: Annotated[BuyInvoiceRepository, Depends(get_buy_invoice_repository)],
    supplier_service: Annotated[SupplierService, Depends(get_supplier_service)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> BuyInvoiceService:
    return BuyInvoiceService(
        repo=buy_invoice_repository,
        supplier_service=supplier_service,
        item_service=item_service,
    )
