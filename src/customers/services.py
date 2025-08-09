from fastapi import status
from src.core.config import settings
from src.core.enums import PartyIdentificationScheme
from .schemas import CustomerOut, CustomerCreate, CustomerUpdate
from .repositories import CustomerRepository
from .exceptions import CustomerNotFoundException

class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo


    async def get(self, id: int) -> CustomerOut:
        customer = await self.customer_repo.get(id)
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)
    
    async def get_customers_for_user(self) -> list[CustomerOut]:
        query_set = await self.customer_repo.get_customers()
        result = [
            CustomerOut.model_validate(customer) for customer in query_set
        ]
        return result
    
    async def create(self, data: CustomerCreate) -> CustomerOut:
        customer = await self.customer_repo.create(data.model_dump())
        return CustomerOut.model_validate(customer)
    
    async def update(self, id: int, data: CustomerUpdate) -> CustomerOut:
        customer = await self.customer_repo.update(id, data.model_dump())
        if not customer:
            raise CustomerNotFoundException()
        return CustomerOut.model_validate(customer)
    
    async def delete(self, id: int) -> None:
        customer = await self.get(id)
        await self.customer_repo.delete(id)
        return None
    