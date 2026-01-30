from .schemas import PointOfSaleOut, PointOfSaleCreate, PointOfSaleUpdate, PointOfSaleFilters
from src.core.schemas import PagintationParams
from .repositories import PointOfSaleRepository
from .exceptions import PointOfSaleNotFoundException
from src.core.schemas.context import RequestContext

class PointOfSaleService:
    def __init__(self, point_of_sale_repo: PointOfSaleRepository):
        self.point_of_sale_repo = point_of_sale_repo

    async def get_point_of_sale(self, ctx: RequestContext, id: int) -> PointOfSaleOut:
        point_of_sale = await self.point_of_sale_repo.get_point_of_sale(ctx.organization.id, ctx.branch.id, id)
        if not point_of_sale:
            raise PointOfSaleNotFoundException()
        return PointOfSaleOut.model_validate(point_of_sale)

    async def get_points_of_sale(self, ctx: RequestContext, pagination_params: PagintationParams, filters: PointOfSaleFilters) -> tuple[int, list[PointOfSaleOut]]:
        total, query_set = await self.point_of_sale_repo.get_points_of_sale(
            ctx.organization.id,
            ctx.branch.id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [PointOfSaleOut.model_validate(point_of_sale) for point_of_sale in query_set]

    async def create_point_of_sale(self, ctx: RequestContext, data: PointOfSaleCreate) -> PointOfSaleOut:
        point_of_sale = await self.point_of_sale_repo.create_point_of_sale(ctx.organization.id, ctx.branch.id, ctx.user.id, data.model_dump())
        return PointOfSaleOut.model_validate(point_of_sale)

    async def update_point_of_sale(self, ctx: RequestContext, id: int, data: PointOfSaleUpdate) -> PointOfSaleOut:
        point_of_sale = await self.point_of_sale_repo.update_point_of_sale(
            ctx.organization.id,
            ctx.branch.id,
            ctx.user.id,
            id,
            data.model_dump(exclude_unset=True),
        )
        if not point_of_sale:
            raise PointOfSaleNotFoundException()
        return PointOfSaleOut.model_validate(point_of_sale)

    async def delete_point_of_sale(self, ctx: RequestContext, id: int) -> None:
        await self.get_point_of_sale(ctx, id)
        await self.point_of_sale_repo.delete_point_of_sale(ctx.organization.id, ctx.branch.id, id)
        return None
