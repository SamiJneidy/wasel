from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .repositories import PointOfSaleRepository
from .services import PointOfSaleService
from src.core.database import get_db


async def get_point_of_sale_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PointOfSaleRepository:
    return PointOfSaleRepository(db)


def get_point_of_sale_service(
    point_of_sale_repo: Annotated[PointOfSaleRepository, Depends(get_point_of_sale_repository)],
) -> PointOfSaleService:
    
    return PointOfSaleService(point_of_sale_repo)
