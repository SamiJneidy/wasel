from .schemas import CustomerOut, CustomerCreate, CustomerUpdate, CustomerFilters
from src.core.schemas import PagintationParams
from .repositories import CustomerRepository
from .exceptions import CustomerNotFoundException
from src.core.schemas.context import RequestContext

class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    async def get_customer(self, ctx: RequestContext, id: int) -> CustomerOut:
        customer = await self.customer_repo.get_customer(ctx.organization.id, id)
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)

    async def get_customers(self, ctx: RequestContext, pagination_params: PagintationParams, filters: CustomerFilters) -> tuple[int, list[CustomerOut]]:
        total, query_set = await self.customer_repo.get_customers(
            ctx.organization.id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [CustomerOut.model_validate(customer) for customer in query_set]

    async def create_customer(self, ctx: RequestContext, data: CustomerCreate) -> CustomerOut:
        customer = await self.customer_repo.create_customer(ctx.organization.id, ctx.user.id, data.model_dump())
        return CustomerOut.model_validate(customer)

    async def update_customer(self, ctx: RequestContext, id: int, data: CustomerUpdate) -> CustomerOut:
        customer = await self.customer_repo.update_customer(ctx.organization.id, ctx.user.id, id, data.model_dump(exclude_unset=True))
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)

    async def delete_customer(self, ctx: RequestContext, id: int) -> None:
        await self.get_customer(ctx, id)
        await self.customer_repo.delete_customer(ctx.organization.id, id)
        return None
