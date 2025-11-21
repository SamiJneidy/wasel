from fastapi import Depends
from typing import Annotated
from ..services.requests_service import AsyncRequestService

def get_requests_service() -> AsyncRequestService:
    return AsyncRequestService()
