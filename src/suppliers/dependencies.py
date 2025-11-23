from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import SupplierRepository
from .services import SupplierService
from src.core.database import get_db


async def get_supplier_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SupplierRepository:
    return SupplierRepository(db)


def get_supplier_service(
    supplier_repo: Annotated[SupplierRepository, Depends(get_supplier_repository)],
) -> SupplierService:
    
    return SupplierService(supplier_repo)
