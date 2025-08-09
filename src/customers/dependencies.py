from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from src.users.schemas import UserOut
from .repositories import CustomerRepository
from .services import CustomerService
from src.core.database import get_db
from src.auth.dependencies import get_current_user


def get_customer_repository(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserOut, Depends(get_current_user)]
) -> CustomerRepository:
    return CustomerRepository(db, user)


def get_customer_service(
    customer_repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
) -> CustomerService:
    
    return CustomerService(customer_repo)
