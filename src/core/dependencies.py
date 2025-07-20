from fastapi import Depends
from .utils import EmailService, AsyncRequestService
from src.core.config import settings


def get_email_service() -> EmailService:
    return EmailService()


def get_request_service() -> AsyncRequestService:
    return AsyncRequestService()
