from src.users.schemas import UserInDB

from .schemas import (
    PointOfSaleOut,
    PointOfSaleCreate,
    PointOfSaleUpdate,
    PointOfSaleFilters,
)
from src.core.schemas import PagintationParams
from .repositories import PointOfSaleRepository
from .exceptions import PointOfSaleNotFoundException


class PointOfSaleService:
    def __init__(self, point_of_sale_repo: PointOfSaleRepository):
        self.point_of_sale_repo = point_of_sale_repo

    async def get(self, user: UserInDB, id: int) -> PointOfSaleOut:
        point_of_sale = await self.point_of_sale_repo.get(user.organization_id, id)
        if not point_of_sale:
            raise PointOfSaleNotFoundException()
        return PointOfSaleOut.model_validate(point_of_sale)

    async def get_points_of_sale(
        self,
        user: UserInDB,
        pagination_params: PagintationParams,
        filters: PointOfSaleFilters,
    ) -> tuple[int, list[PointOfSaleOut]]:
        total, query_set = await self.point_of_sale_repo.get_points_of_sale(
            user.organization_id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [PointOfSaleOut.model_validate(point_of_sale) for point_of_sale in query_set]

    async def create(self, user: UserInDB, data: PointOfSaleCreate) -> PointOfSaleOut:
        point_of_sale = await self.point_of_sale_repo.create(
            user.organization_id,
            user.id,
            data.model_dump(),
        )
        return PointOfSaleOut.model_validate(point_of_sale)

    async def update(
        self,
        user: UserInDB,
        id: int,
        data: PointOfSaleUpdate,
    ) -> PointOfSaleOut:
        point_of_sale = await self.point_of_sale_repo.update(
            user.organization_id,
            user.id,
            id,
            data.model_dump(exclude_unset=True),
        )
        if not point_of_sale:
            raise PointOfSaleNotFoundException()
        return PointOfSaleOut.model_validate(point_of_sale)

    async def delete(self, user: UserInDB, id: int) -> None:
        await self.get(user, id)
        await self.point_of_sale_repo.delete(user.organization_id, id)
        return None
