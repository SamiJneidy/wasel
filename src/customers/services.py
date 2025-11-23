from fastapi import status
from src.core.config import settings
from src.core.enums import PartyIdentificationScheme
from src.users.schemas import UserInDB

from .schemas import (
    CustomerOut,
    CustomerCreate,
    CustomerUpdate,
    CustomerFilters,
)
from src.core.schemas import PagintationParams
from .repositories import CustomerRepository
from .exceptions import CustomerNotFoundException


class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    async def get(self, user: UserInDB, id: int) -> CustomerOut:
        customer = await self.customer_repo.get(user.organization_id, id)
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)

    async def get_customers_for_user(
        self,
        user: UserInDB,
        pagination_params: PagintationParams,
        filters: CustomerFilters,
    ) -> tuple[int, list[CustomerOut]]:
        total, query_set = await self.customer_repo.get_customers(
            user.organization_id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [CustomerOut.model_validate(customer) for customer in query_set]

    async def create(self, user: UserInDB, data: CustomerCreate) -> CustomerOut:
        print(user.id)
        customer = await self.customer_repo.create(user.organization_id, user.id, data.model_dump())
        return CustomerOut.model_validate(customer)

    async def update(
        self,
        user: UserInDB,
        id: int,
        data: CustomerUpdate,
    ) -> CustomerOut:
        customer = await self.customer_repo.update(
            user.organization_id,
            user.id,
            id,
            data.model_dump(exclude_unset=True),
        )
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)

    async def delete(self, user: UserInDB, id: int) -> None:
        await self.get(user, id)
        await self.customer_repo.delete(user.organization_id, id)
        return None
