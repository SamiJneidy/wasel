from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from src.users.schemas import UserOut
from .repositories import SupplierRepository
from .services import SupplierService
from src.core.database import get_db
from src.auth.dependencies import get_current_user


def get_supplier_repository(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserOut, Depends(get_current_user)]
) -> SupplierRepository:
    return SupplierRepository(db, user)


def get_supplier_service(
    supplier_repo: Annotated[SupplierRepository, Depends(get_supplier_repository)],
) -> SupplierService:
    
    return SupplierService(supplier_repo)
