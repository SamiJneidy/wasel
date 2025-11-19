from fastapi import status
from src.core.config import settings
from src.core.enums import PartyIdentificationScheme
from .schemas import CustomerOut, CustomerCreate, CustomerUpdate, PagintationParams, CustomerFilters
from .repositories import CustomerRepository
from .exceptions import CustomerNotFoundException

class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo


    async def get(self, user_id: int, id: int) -> CustomerOut:
        customer = await self.customer_repo.get(user_id, id)
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)
    
    async def get_customers_for_user(self, user_id: int, pagination_params: PagintationParams, filters: CustomerFilters) -> list[CustomerOut]:
        total, query_set = await self.customer_repo.get_customers(user_id, pagination_params.skip, pagination_params.limit, filters.model_dump(exclude_none=True))
        return total, [CustomerOut.model_validate(customer) for customer in query_set]
    
    async def create(self, user_id: int, data: CustomerCreate) -> CustomerOut:
        customer = await self.customer_repo.create(user_id, data.model_dump())
        return CustomerOut.model_validate(customer)
    
    async def update(self, user_id: int, id: int, data: CustomerUpdate) -> CustomerOut:
        customer = await self.customer_repo.update(user_id, id, data.model_dump())
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)
    
    async def delete(self, user_id: int, id: int) -> None:
        customer = await self.get(user_id, id)
        await self.customer_repo.delete(user_id, id)
        return None
    