from src.core.config import settings
from src.core.enums import PartyIdentificationScheme
from src.core.schemas import PagintationParams
from .schemas import SupplierOut, SupplierCreate, SupplierUpdate, SupplierFilters
from .repositories import SupplierRepository
from .exceptions import SupplierNotFoundException
from src.core.schemas.context import RequestContext

class SupplierService:
    def __init__(self, supplier_repo: SupplierRepository):
        self.supplier_repo = supplier_repo

    async def get_supplier(self, ctx: RequestContext, id: int) -> SupplierOut:
        supplier = await self.supplier_repo.get_supplier(ctx.organization.id, id)
        if not supplier:
            raise SupplierNotFoundException()
        return SupplierOut.model_validate(supplier)

    async def get_suppliers(self, ctx: RequestContext, pagination_params: PagintationParams, filters: SupplierFilters) -> tuple[int, list[SupplierOut]]:
        total, query_set = await self.supplier_repo.get_suppliers(
            ctx.organization.id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [SupplierOut.model_validate(supplier) for supplier in query_set]

    async def create_supplier(self, ctx: RequestContext, data: SupplierCreate) -> SupplierOut:
        supplier = await self.supplier_repo.create_supplier(ctx.organization.id, ctx.user.id, data.model_dump())
        return SupplierOut.model_validate(supplier)

    async def update_supplier(self, ctx: RequestContext, id: int, data: SupplierUpdate) -> SupplierOut:
        supplier = await self.supplier_repo.update_supplier(ctx.organization.id, ctx.user.id, id, data.model_dump(exclude_unset=True))
        if not supplier:
            raise SupplierNotFoundException()
        return SupplierOut.model_validate(supplier)

    async def delete_supplier(self, ctx: RequestContext, id: int) -> None:
        await self.get_supplier(ctx, id)
        await self.supplier_repo.delete_supplier(ctx.organization.id, id)
        return None
