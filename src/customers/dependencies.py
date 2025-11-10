from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from src.users.schemas import UserOut
from .repositories import CustomerRepository
from .services import CustomerService
from src.core.database import get_db
from src.users.dependencies import UserService, get_user_service
from src.core.dependencies import get_current_user


async def get_customer_repository(
    db: Annotated[Session, Depends(get_db)],
    user_email: Annotated[str, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> CustomerRepository:
    user = await user_service.get_by_email(user_email)
    return CustomerRepository(db, user)


def get_customer_service(
    customer_repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
) -> CustomerService:
    
    return CustomerService(customer_repo)
