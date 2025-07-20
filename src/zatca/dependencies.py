from fastapi import Depends
from typing import Annotated
from .services import ZatcaService
from src.core.utils import AsyncRequestService
from src.core.dependencies import get_request_service


def get_zatca_service(request_service: Annotated[AsyncRequestService, Depends(get_request_service)]) -> ZatcaService:
    return ZatcaService(request_service)
