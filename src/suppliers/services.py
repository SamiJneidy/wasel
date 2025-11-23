from src.core.config import settings
from src.core.enums import PartyIdentificationScheme
from src.users.schemas import UserInDB
from src.core.schemas import PagintationParams
from .schemas import (
    SupplierOut,
    SupplierCreate,
    SupplierUpdate,
    SupplierFilters,
)
from .repositories import SupplierRepository
from .exceptions import SupplierNotFoundException


class SupplierService:
    def __init__(self, supplier_repo: SupplierRepository):
        self.supplier_repo = supplier_repo

    async def get(self, user: UserInDB, id: int) -> SupplierOut:
        supplier = await self.supplier_repo.get(user.organization_id, id)
        if not supplier:
            raise SupplierNotFoundException()
        return SupplierOut.model_validate(supplier)

    async def get_suppliers_for_user(
        self,
        user: UserInDB,
        pagination_params: PagintationParams,
        filters: SupplierFilters,
    ) -> tuple[int, list[SupplierOut]]:
        total, query_set = await self.supplier_repo.get_suppliers(
            user.organization_id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [SupplierOut.model_validate(supplier) for supplier in query_set]

    async def create(self, user: UserInDB, data: SupplierCreate) -> SupplierOut:
        supplier = await self.supplier_repo.create(
            user.organization_id,
            user.id,
            data.model_dump(),
        )
        return SupplierOut.model_validate(supplier)

    async def update(
        self,
        user: UserInDB,
        id: int,
        data: SupplierUpdate,
    ) -> SupplierOut:
        supplier = await self.supplier_repo.update(
            user.organization_id,
            user.id,
            id,
            data.model_dump(exclude_unset=True),
        )
        if not supplier:
            raise SupplierNotFoundException()
        return SupplierOut.model_validate(supplier)

    async def delete(self, user: UserInDB, id: int) -> None:
        await self.get(user, id)
        await self.supplier_repo.delete(user.organization_id, id)
        return None
