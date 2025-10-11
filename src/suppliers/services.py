from fastapi import status
from src.core.config import settings
from src.core.enums import PartyIdentificationScheme
from .schemas import SupplierOut, SupplierCreate, SupplierUpdate, PagintationParams, SupplierFilters
from .repositories import SupplierRepository
from .exceptions import SupplierNotFoundException

class SupplierService:
    def __init__(self, supplier_repo: SupplierRepository):
        self.supplier_repo = supplier_repo


    async def get(self, id: int) -> SupplierOut:
        supplier = await self.supplier_repo.get(id)
        if not supplier:
            raise SupplierNotFoundException()
        return SupplierOut.model_validate(supplier)
    
    async def get_suppliers_for_user(self, pagination_params: PagintationParams, filters: SupplierFilters) -> list[SupplierOut]:
        total, query_set = await self.supplier_repo.get_suppliers(pagination_params.skip, pagination_params.limit, filters.model_dump(exclude_none=True))
        return total, [SupplierOut.model_validate(customer) for customer in query_set]
    
    async def create(self, data: SupplierCreate) -> SupplierOut:
        supplier = await self.supplier_repo.create(data.model_dump())
        return SupplierOut.model_validate(supplier)
    
    async def update(self, id: int, data: SupplierUpdate) -> SupplierOut:
        supplier = await self.supplier_repo.update(id, data.model_dump())
        if not supplier:
            raise SupplierNotFoundException()
        return SupplierOut.model_validate(supplier)
    
    async def delete(self, id: int) -> None:
        supplier = await self.get(id)
        await self.supplier_repo.delete(id)
        return None
    