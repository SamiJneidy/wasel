from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import CustomerRepository
from .services import CustomerService
from src.core.database import get_db
from src.users.dependencies import UserService, get_user_service


async def get_customer_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CustomerRepository:
    return CustomerRepository(db)


def get_customer_service(
    customer_repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
) -> CustomerService:
    
    return CustomerService(customer_repo)
